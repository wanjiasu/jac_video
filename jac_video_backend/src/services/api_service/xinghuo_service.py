import aiohttp
import time
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import os
import sys
from typing import Tuple, Dict, List
import math

# 将项目根目录添加到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(project_root)

from src.services.api_service.xinghuo_config import xinghuo_text_dict, xinghuo_image_config

# 文字生成相关函数
async def get_response_from_model(word, model_name):
    """
    从星火大模型获取文字响应
    :param word: 输入的单词
    :param model_name: 模型名称
    :return: 处理后的内容和使用情况
    """
    # 根据模型名称获取配置
    model_config = xinghuo_text_dict.get(model_name)
    print(model_config)
    if not model_config:
        raise ValueError("无效的模型名称")

    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    data = {
        "max_tokens": 4096,
        "top_k": 4,
        "temperature": 0.5,
        "messages": [
            {
                "role": "system",
                "content": """
                    你是一位严谨的日语教师，擅长运用联想记忆法帮助学生学习词汇。现在，请你根据用户给出的日语单词，联想并给出 6 个相关的日语单词，并提供这些单词的罗马音和中文翻译。请务必保证罗马音的准确性。返回结果请使用 JSON 格式。

                    ## 输入内容
                    用户给出的日语单词

                    ## 步骤
                    1. **词汇联想:** 根据用户输入的单词，运用联想记忆法，生成 6 个相关的日语单词。请避免直接使用用户输入的单词。
                    2. **初次生成JSON:** 将联想到的 6 个单词、它们的罗马音和中文翻译，按照指定的 JSON Schema 结构生成 JSON 结果。
                    3. **罗马音校对:** 仔细核对 JSON 结果中每个日语单词及其对应的罗马音是否完全一致。**请使用可靠的罗马音转换工具或者你的专业知识进行校对。**
                    4. **纠正与二次生成:** 如果发现任何一个罗马音错误，立即纠正错误并重新生成整个 JSON 结果。
                    5. **二次校对与确认:** 再次核对新生成的 JSON 结果中的罗马音。
                    6. **（循环）三次校对与最终确认:** 如果仍发现错误，再次重复步骤4和5，最多循环两次。确保最终输出的 JSON 结果中的罗马音完全正确。


                    ## 输出内容
                    按照如下 JSON Schema 结构输出 JSON 结果：

                    ```json
                    {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "center_word": "用户输入的单词",
                        "center_word_romaji": "用户输入的单词的罗马音",
                        "center_word_translation": "用户输入的单词的中文翻译",
                        "surrounding_words": ["周围单词1", "周围单词2", "周围单词3", "周围单词4", "周围单词5", "周围单词6"],
                        "surrounding_words_romaji": ["周围单词1的罗马音", "周围单词2的罗马音", "周围单词3的罗马音", "周围单词4的罗马音", "周围单词5的罗马音", "周围单词6的罗马音"],
                        "surrounding_words_translation": ["周围单词1的中文翻译", "周围单词2的中文翻译", "周围单词3的中文翻译", "周围单词4的中文翻译", "周围单词5的中文翻译", "周围单词6的中文翻译"]
                    }
                    """
            },
            {
                "role": "user",
                "content": word
            }
        ],
        "model": model_config["model"]
    }
    headers = {
        "Authorization": model_config["APIPassword"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            response_text = await response.text()
            for line in response_text.split('\n'):
                if line:
                    try:
                        json_response = json.loads(line)
                        if json_response.get("code") == 0:
                            content_str = json_response["choices"][0]["message"]["content"]
                            content_str = content_str.replace("```json\n", "").replace("\n```", "")
                            content_dict = json.loads(content_str)
                            usage_dict = json_response["usage"]
                            return content_dict, usage_dict
                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        print(f"Error parsing response: {e}")
                        continue
    return None, None

# 图片生成相关类和函数
class AssembleHeaderException(Exception):
    """URL组装异常类"""
    def __init__(self, msg):
        self.message = msg

class Url:
    """URL解析类"""
    def __init__(self, host, path, schema):
        self.host = host
        self.path = path
        self.schema = schema

def parse_url(request_url):
    """
    解析URL，分离出host、path和schema
    :param request_url: 完整的URL
    :return: Url对象
    """
    stidx = request_url.index("://")
    host = request_url[stidx + 3:]
    schema = request_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + request_url)
    path = host[edidx:]
    host = host[:edidx]
    return Url(host, path, schema)

def assemble_ws_auth_url(request_url, method="GET", api_key="", api_secret=""):
    """
    组装带有认证信息的WebSocket URL
    :param request_url: 原始URL
    :param method: HTTP方法
    :param api_key: API密钥
    :param api_secret: API密钥对应的secret
    :return: 带认证信息的URL
    """
    u = parse_url(request_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                            digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }
    return request_url + "?" + urlencode(values)

async def generate_image(width: int, height: int, desc: str) -> str:
    """
    调用星火大模型生成图片并保存到本地
    :param width: 图片宽度
    :param height: 图片高度
    :param desc: 图片描述
    :return: 图片访问地址
    """
    try:
        # 获取配置
        appid = xinghuo_image_config["APPID"]
        api_secret = xinghuo_image_config["APISecret"]
        api_key = xinghuo_image_config["APIKEY"]
        
        # 生成请求URL和内容
        host = 'http://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti'
        url = assemble_ws_auth_url(host, method='POST', api_key=api_key, api_secret=api_secret)
        
        # 生成请求体
        body = {
            "header": {
                "app_id": appid,
                "uid": "123456789"
            },
            "parameter": {
                "chat": {
                    "domain": "general",
                    "temperature": 0.5,
                    "max_tokens": 4096,
                    "width": width,
                    "height": height
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {
                            "role": "user",
                            "content": desc
                        }
                    ]
                }
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers={'content-type': "application/json"}) as response:
                response_text = await response.text()
                data = json.loads(response_text)
                
                if data['header']['code'] != 0:
                    raise Exception(f'请求错误: {data["header"]["code"]}, {data}')
                
                # 解析响应获取图片数据
                text = data["payload"]["choices"]["text"]
                image_content = text[0]
                image_base = image_content["content"]
                
                # 生成唯一文件名并保存图片
                timestamp = int(time.time() * 1000)
                image_name = f"img_{timestamp}"
                
                # 修改保存路径：使用项目根目录下的 static/images
                save_dir = os.path.join(project_root, "static", "images")
                os.makedirs(save_dir, exist_ok=True)
                image_path = os.path.join(save_dir, f"{image_name}.jpg")
                
                # 将base64数据解码并保存为图片文件
                image_data = base64.b64decode(image_base)
                with open(image_path, "wb") as f:
                    f.write(image_data)
                
                # 返回可访问的图片地址
                return f"/static/images/{image_name}.jpg"
                
    except Exception as e:
        raise Exception(f"生成图片失败: {str(e)}")

# 预定义的分辨率列表
RESOLUTIONS = [
    (512, 512),   # 1:1
    (640, 360),   # 16:9
    (640, 480),   # 4:3
    (640, 640),   # 1:1
    (680, 512),   # 4:3 约
    (512, 680),   # 3:4 约
    (768, 768),   # 1:1
    (720, 1280),  # 9:16
    (1280, 720),  # 16:9
    (1024, 1024)  # 1:1
]

async def generate_image_with_resolution(resolution: str, aspect_ratio: str, orientation: str, desc: str) -> str:
    """
    根据指定的分辨率、宽高比和方向生成图片
    :param resolution: 目标分辨率（如 "720p", "1080p"）
    :param aspect_ratio: 宽高比（如 "16:9", "4:3", "1:1"）
    :param orientation: 方向（"landscape" 横向或 "portrait" 竖向）
    :param desc: 图片描述
    :return: 图片访问地址
    """
    desc = f"生成一个{desc}, 卡通风格, 清新风格 ## 限制 1. 主题颜色尽量为灰色或者白色 2. 整体尽量简洁, 只要出现少量元素"
    try:
        # 解析目标分辨率
        target_height = int(resolution.lower().replace("p", ""))
        
        # 解析宽高比
        width_ratio, height_ratio = map(int, aspect_ratio.split(":"))
        
        # 计算目标宽度
        target_width = int(target_height * width_ratio / height_ratio)
        
        # 如果是竖向，交换宽高
        if orientation.lower() == "portrait":
            target_width, target_height = target_height, target_width
        
        # 计算目标面积
        target_area = target_width * target_height
        
        # 找到最接近的预定义分辨率
        closest_resolution = min(
            RESOLUTIONS,
            key=lambda res: (
                abs(res[0] * res[1] - target_area) +
                abs(res[0]/res[1] - target_width/target_height) * target_area
            )
        )
        
        # 打印调试信息
        print(f"目标分辨率: {target_width}x{target_height}")
        print(f"选择的分辨率: {closest_resolution[0]}x{closest_resolution[1]}")
        
        # 生成图片
        image_url = await generate_image(  # 确保 generate_image 是异步函数
            width=closest_resolution[0],
            height=closest_resolution[1],
            desc=desc
        )
        
        return "http://localhost:5000"+image_url
        
    except Exception as e:
        raise Exception(f"生成图片失败: {str(e)}")

# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test():
        try:
            # 测试文字生成
            content, usage = await get_response_from_model("食べる", "Spark Max")
            print("文字生成结果:", json.dumps(content, ensure_ascii=False, indent=2))
            
            # # 测试不同的分辨率和方向
            # tests = [
            #     ("720p", "16:9", "landscape", "一只可爱的猫咪"),
            #     # ("720p", "16:9", "portrait", "一座高耸的塔"),
            #     ("1080p", "4:3", "landscape", "一片蓝天白云"),
            # ]
            
            # for test in tests:
            #     result = await generate_image_with_resolution(*test)
            #     print(f"测试参数: {test}")
            #     print(f"生成的图片地址: {result}\n")
                
        except Exception as e:
            print(f"错误: {str(e)}")
    
    asyncio.run(test())