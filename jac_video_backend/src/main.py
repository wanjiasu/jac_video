from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import time
import random

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from src.routers.japanese_vocab import router as japanese_vocab_router
from config import ALLOW_ORIGINS

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,  # 使用导入的配置
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 确保所有静态资源目录存在
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
images_dir = os.path.join(static_dir, "images")
os.makedirs(images_dir, exist_ok=True)
voices_dir = os.path.join(static_dir, "voices")
os.makedirs(voices_dir, exist_ok=True)
bgm_dir = os.path.join(static_dir, "bgm")
os.makedirs(bgm_dir, exist_ok=True)

# 设置目录权限
try:
    for directory in [static_dir, images_dir, voices_dir, bgm_dir]:
        os.chmod(directory, 0o755)
except Exception as e:
    print(f"Warning: Could not set directory permissions: {e}")

# 配置静态文件服务，添加一些额外的配置
app.mount("/static", StaticFiles(
    directory=static_dir,
    check_dir=True,  # 检查目录是否存在
    html=True  # 允许访问 HTML 文件
), name="static")

@app.get("/")
async def root():
    return {"message": "Hello World"}

# 包含路由
app.include_router(japanese_vocab_router)

@app.get("/test-static")
async def test_static():
    # 列出 static/images 目录中的文件
    images_dir = os.path.join(static_dir, "images")
    files = os.listdir(images_dir)
    return {
        "static_dir": static_dir,
        "images_dir": images_dir,
        "files": files,
        "permissions": {
            "static_dir": oct(os.stat(static_dir).st_mode)[-3:],
            "images_dir": oct(os.stat(images_dir).st_mode)[-3:]
        }
    }

@app.post("/upload-image")
async def upload_image(file: UploadFile):
    # ... 处理文件上传
    filename = file.filename
    file_path = f"/static/images/{filename}"  # 只返回相对路径
    return {"image_url": file_path}

@app.post("/products/japanese-vocab/step3/get_image_by_model")
async def get_image_by_model():
    # ... 其他代码 ...
    timestamp = int(time.time() * 1000)  # 添加时间戳导入
    image_url = f"/static/images/img_{timestamp}.jpg"
    return {"image_url": image_url}  # 返回相对路径

# 添加一个辅助函数来处理 URL 到本地路径的转换
def url_to_local_path(url: str) -> str:
    """将 URL 转换为本地文件路径"""
    if url.startswith('http'):
        # 提取 URL 中的路径部分（/static/bgm/bg2.MP3）
        path = url.split('/static/', 1)[1] if '/static/' in url else ''
        # 转换为本地路径
        return os.path.join(static_dir, path)
    return url

# 在处理音乐文件的地方用这个函数
@app.get("/products/japanese-vocab/step4/get_random_bgm")
async def get_random_bgm():
    try:
        # 在Docker环境中，直接使用固定路径
        # 容器中音乐文件在 /app/static/bgm 目录
        container_bgm_dir = "/app/static/bgm"
        print(f"Current working directory: {os.getcwd()}")
        print(f"Using fixed BGM directory: {container_bgm_dir}")
        print(f"Directory exists: {os.path.exists(container_bgm_dir)}")
        
        # 列出目录内容
        try:
            dir_contents = os.listdir(container_bgm_dir)
            print(f"Directory contents: {dir_contents}")
        except Exception as e:
            print(f"Error listing directory: {e}")
            dir_contents = []
        
        # 获取 bgm 目录下的所有音乐文件（不区分大小写）
        bgm_files = [f for f in dir_contents if f.lower().endswith(('.mp3', '.wav', '.MP3', '.WAV'))]
        print(f"Found BGM files: {bgm_files}")
        
        if not bgm_files:
            raise HTTPException(
                status_code=404,
                detail=f"没有可用的背景音乐文件。目录：{container_bgm_dir}，文件列表：{dir_contents}"
            )
        
        # 随机选择一个音乐文件
        selected_bgm = random.choice(bgm_files)
        bgm_url = f"/static/bgm/{selected_bgm}"
        
        # 验证文件是否真实存在
        full_path = os.path.join(container_bgm_dir, selected_bgm)
        print(f"Selected BGM full path: {full_path}")
        print(f"File exists: {os.path.exists(full_path)}")
        print(f"File size: {os.path.getsize(full_path) if os.path.exists(full_path) else 'N/A'}")
        
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=404,
                detail=f"选中的音乐文件不存在：{selected_bgm}"
            )
        
        return {"music_url": bgm_url}
        
    except Exception as e:
        print(f"Error in get_random_bgm: {str(e)}")
        # 返回更详细的错误信息
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/test-bgm")
async def test_bgm():
    try:
        bgm_dir = os.path.join(static_dir, "bgm")
        # 列出目录内容
        files = os.listdir(bgm_dir)
        # 检查特定文件
        test_file = "bg2.MP3"
        test_path = os.path.join(bgm_dir, test_file)
        
        return {
            "bgm_dir": bgm_dir,
            "directory_exists": os.path.exists(bgm_dir),
            "is_directory": os.path.isdir(bgm_dir),
            "files_in_directory": files,
            "test_file_exists": os.path.exists(test_path),
            "test_file_path": test_path,
            "directory_permissions": oct(os.stat(bgm_dir).st_mode)[-3:],
            "file_permissions": oct(os.stat(test_path).st_mode)[-3:] if os.path.exists(test_path) else None
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0",  # 允许所有IP访问
        port=5001
    )
