# JAC Video Project

这是一个用于生成日语词汇学习视频的全栈应用程序。

## 项目结构

- `jac_video_frontend/`: Next.js 前端应用
- `jac_video_backend/`: FastAPI 后端服务

## 开发环境设置

### 前端设置

1. 进入前端目录：
```bash
cd jac_video_frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

### 后端设置

1. 进入后端目录：
```bash
cd jac_video_backend
```

2. 创建并激活虚拟环境：
```bash
python -m venv env
source env/bin/activate  # Unix/macOS
# 或
.\env\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 启动后端服务：
```bash
uvicorn src.main:app --reload --port 5001
```

## 使用 Docker

项目可以使用 Docker Compose 运行：

```bash
docker-compose up --build
```

## 环境变量

请确保在运行项目之前设置了必要的环境变量：

### 后端环境变量
- 在 `jac_video_backend/config.py` 中配置相关 API 密钥

```bash
mv jac_video_backend/config.py.example jac_video_backend/config.py
```

### 前端环境变量
- 在 `jac_video_frontend/.env.local` 中配置 API 地址
mv jac_video_frontend/.env.example jac_video_frontend/.env
```bash

```

## 功能特性

- 日语词汇学习视频生成
- AI 驱动的内容生成
- 文本转语音
- 图片生成
- 视频合成

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE) 