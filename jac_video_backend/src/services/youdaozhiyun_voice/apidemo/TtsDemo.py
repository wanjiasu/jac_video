import requests
import os
import sys
from pathlib import Path
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Optional
import json

# 获取项目根目录
project_root = str(Path(__file__).resolve().parents[4])
if project_root not in sys.path:
    sys.path.append(project_root)

from src.services.youdaozhiyun_voice.utils.AuthV3Util import addAuthParams

# 您的应用ID
APP_KEY = '5fedf71ebe8aa998'
# 您的应用密钥
APP_SECRET = 'hpAgPSgTRZaBTXBQA2pgmAFcvnPXnMTS'

# 音频文件存储目录
VOICES_DIR = os.path.join(project_root, 'static', 'voices')
if not os.path.exists(VOICES_DIR):
    os.makedirs(VOICES_DIR)

def create_retry_session(
    retries: int = 3,
    backoff_factor: float = 2.0,
    status_forcelist: tuple = (411, 500, 502, 503, 504),
    allowed_methods: frozenset = frozenset(['GET', 'POST'])
) -> requests.Session:
    """
    创建一个带有重试机制的 requests session
    
    Args:
        retries: 最大重试次数
        backoff_factor: 重试延迟因子，每次重试等待时间 = backoff_factor * (2 ** (retry - 1))
                       例如：第1次重试等待2秒，第2次等待4秒，第3次等待8秒
        status_forcelist: 需要重试的HTTP状态码
        allowed_methods: 允许重试的HTTP方法
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
        backoff_jitter=0,
        respect_retry_after_header=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def doCall(url: str, header: dict, params: dict, method: str) -> Optional[requests.Response]:
    """
    执行 HTTP 请求，带有重试机制
    """
    session = create_retry_session()
    try:
        if method == 'get':
            response = session.get(url, params=params, headers=header, timeout=10)
        elif method == 'post':
            response = session.post(url, data=params, headers=header, timeout=10)
        
        # 检查是否是 411 错误，如果是则抛出异常触发重试
        if response.status_code == 411:
            raise requests.exceptions.RetryError(f"Rate limit exceeded (411)")
            
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed, attempt will be retried: {e}")
        return None
    finally:
        session.close()

def createRequest(text: str, retry_count: int = 3) -> Optional[str]:
    """
    生成语音文件并返回可访问的URL
    
    Args:
        text: 要转换为语音的文本
        retry_count: 最大重试次数
    Returns:
        Optional[str]: 生成的语音文件URL，失败时返回None
    """
    for attempt in range(retry_count):
        try:
            # 检查是否已经存在相同文本的语音文件
            existing_files = [f for f in os.listdir(VOICES_DIR) if f.endswith('.mp3')]
            for file in existing_files:
                if text in file:  # 如果文件名包含要转换的文本
                    print(f"Found existing audio file for text: {text}")
                    return f"/static/voices/{file}"

            voiceName = 'youkejiang'
            format = 'mp3'

            data = {'q': text, 'voiceName': voiceName, 'format': format, 'speed': 1}
            addAuthParams(APP_KEY, APP_SECRET, data)

            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            res = doCall('https://openapi.youdao.com/ttsapi', header, data, 'post')
            
            if not res:
                wait_time = 2 ** attempt * 2  # 2秒, 4秒, 8秒
                print(f"Request failed, waiting {wait_time} seconds before retry {attempt + 1}/{retry_count}")
                time.sleep(wait_time)
                continue

            if res.headers.get('Content-Type', '').startswith('audio'):
                # 生成包含文本的文件名，方便后续复用
                filename = f"tts_{text}_{int(time.time()*1000)}.mp3"
                file_path = os.path.join(VOICES_DIR, filename)
                
                # 保存文件
                with open(file_path, 'wb') as f:
                    f.write(res.content)
                
                # 返回可访问的URL
                return f"/static/voices/{filename}"
            else:
                error_data = json.loads(res.content.decode('utf-8'))
                error_code = error_data.get('errorCode')
                
                # 如果是频率限制错误，等待后重试
                if error_code == '411':
                    wait_time = 2 ** attempt * 2  # 2秒, 4秒, 8秒
                    print(f"Rate limit reached, waiting {wait_time} seconds before retry {attempt + 1}/{retry_count}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API Error: {res.content.decode('utf-8')}")
                    return None

        except Exception as e:
            print(f"Error in createRequest (attempt {attempt + 1}/{retry_count}): {e}")
            if attempt < retry_count - 1:  # 如果不是最后一次尝试
                wait_time = 2 ** attempt * 2
                print(f"Waiting {wait_time} seconds before retry")
                time.sleep(wait_time)
            else:
                return None

    print(f"Failed to generate audio after {retry_count} attempts")
    return None

def batch_create_requests(texts: list[str]) -> dict[str, Optional[str]]:
    """
    批量生成语音文件并返回URL映射
    
    Args:
        texts: 要转换的文本列表
    Returns:
        dict[str, Optional[str]]: 文本到URL的映射
    """
    results = {}
    for text in texts:
        print(f"\nProcessing text: {text}")
        url = createRequest(text)
        results[text] = url
        # 每次请求后等待1秒，避免触发频率限制
        time.sleep(1)
    return results

# 测试用例
if __name__ == '__main__':
    url = createRequest("料理")
    print(f"Generated audio URL: {url}")
