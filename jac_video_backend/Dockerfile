# jac_video_backend/Dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 使用清华大学镜像源
RUN echo \
    deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware\n\
    deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware\n\
    deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware\n\
    deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware\
    > /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装开发依赖
RUN pip install --no-cache-dir watchdog

# 创建必要的目录并设置权限
RUN mkdir -p /app/static/images \
    /app/static/voices \
    /app/static/bgm \
    && chmod -R 755 /app/static

# 复制默认的 BGM 文件（如果有的话）
COPY static/bgm/* /app/static/bgm/

# 暴露端口
EXPOSE 5001

# 默认使用开发模式启动，可以被 docker-compose 中的 command 覆盖
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]