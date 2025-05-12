# JAC Video Project

这是一个用于生成日语词汇学习视频的全栈应用程序。

## 项目结构

- `jac_video_frontend/`: Next.js 前端应用
- `jac_video_backend/`: FastAPI 后端服务
- `use_example.mp4`: 使用示例视频

## 使用示例

https://github.com/user-attachments/assets/5ddbe4f2-16d4-4049-85be-3c69522704af

项目根目录下的 `use_example.mp4` 展示了完整的使用流程：

1. 设置标题和形状
2. 输入日语单词并生成相关内容
3. 选择或生成背景图片
4. 添加背景音乐
5. 生成语音内容
6. 最终视频合成

您可以观看此视频快速了解系统的主要功能和操作方法。

## 试用地址
http://59.110.32.252:3000/

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
cp jac_video_backend/config.py.example jac_video_backend/config.py
```

### 前端环境变量
- 在 `jac_video_frontend/.env.local` 中配置 API 地址

```bash
cp jac_video_frontend/.env.example jac_video_frontend/.env
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