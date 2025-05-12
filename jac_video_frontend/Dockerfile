# jac_video_frontend/Dockerfile
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 在开发模式下，我们不需要复制源代码和构建
# 源代码将通过 volume 挂载

# 暴露端口
EXPOSE 3000

# 默认使用开发模式启动，可以被 docker-compose 中的 command 覆盖
CMD ["npm", "run", "dev"]