# JAC Video Backend - AI视频生成服务

## 🌟 项目简介
JAC Video Backend 是一个基于 FastAPI 的视频生成服务后端，专注于生成日语教学视频内容。本服务提供了完整的视频生成流水线，包括文本处理、图片生成、音频合成和视频合成等功能。

## 🛠️ 技术栈
- FastAPI: 高性能 Web 框架
- OpenCV & MoviePy: 视频处理引擎
- Pydub: 专业音频处理
- Pillow: 图片处理库
- Python 3.11+

## 🚀 快速部署指南

### 环境要求
- Python >= 3.11
- FFmpeg
- 足够的磁盘空间（建议 > 10GB）
- 内存 >= 4GB

### 本地开发部署

1. **克隆项目**
```bash
git clone [your-repository-url]
cd jac_video_backend
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **安装 FFmpeg**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# MacOS
brew install ffmpeg

# Windows
# 下载 FFmpeg 并添加到系统环境变量
```

5. **配置环境变量**
创建 `.env` 文件：
```bash
# 服务配置
APP_ENV=development
PORT=8000
HOST=0.0.0.0

# 文件存储路径
STATIC_PATH=static
VIDEO_PATH=static/videos
VOICE_PATH=static/voices
IMAGE_PATH=static/images

# API密钥（如果需要）
API_KEY=your_api_key
```

6. **初始化存储目录**
```bash
mkdir -p static/videos static/voices static/images
```

7. **启动服务**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境部署

#### 方法一：使用 Gunicorn（推荐）

1. **安装 Gunicorn**
```bash
pip install gunicorn
```

2. **创建 Gunicorn 配置文件 `gunicorn_conf.py`**
```python
workers = 4
bind = "0.0.0.0:8000"
timeout = 120
```

3. **启动服务**
```bash
gunicorn -c gunicorn_conf.py src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 方法二：使用 Docker 部署

1. **构建镜像**
```bash
docker build -t jac-video-backend .
```

2. **运行容器**
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/static:/app/static \
  --name jac-video-backend \
  jac-video-backend
```

## 📁 项目结构
```
jac_video_backend/
├── src/
│   ├── main.py           # 应用入口
│   ├── routers/          # API路由
│   ├── services/         # 业务服务
│   │   ├── video_process/    # 视频处理
│   │   └── api_service/      # 外部API服务
│   └── core/            # 核心配置
├── static/              # 静态资源
│   ├── videos/         # 视频文件
│   ├── voices/         # 音频文件
│   └── images/         # 图片文件
└── tests/              # 测试文件
```

## 🔧 常见问题解决

### 1. FFmpeg相关问题
```bash
# 检查FFmpeg安装
ffmpeg -version

# 常见错误：找不到FFmpeg
# 解决：确保FFmpeg在系统PATH中
```

### 2. 存储空间问题
- 定期清理 `static` 目录
- 设置自动清理脚本
```bash
# 示例清理脚本
find static/videos -mtime +7 -type f -delete
```

### 3. 性能优化建议
- 使用 nginx 做反向代理
- 配置适当的缓存策略
- 使用异步任务处理长时间运行的任务

## 📝 API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔍 监控和日志
- 日志位置: `logs/app.log`
- 监控指标: `/metrics` (如果启用)

## 🤝 技术支持
- 问题反馈：[GitHub Issues](your-issues-url)
- 邮件支持：[your-email@example.com]

## 📜 许可证
[MIT License](LICENSE)
"""



