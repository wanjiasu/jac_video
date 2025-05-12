#!/bin/bash

# 生产环境部署脚本
echo "===== JAC Video 生产环境部署脚本 ====="

# 准备目录
echo "1. 准备必要的目录..."
mkdir -p nginx/ssl
mkdir -p backups

# 检查Next.js配置文件
if [ ! -f "init-next-config.js" ]; then
    echo "2. 创建Next.js配置文件..."
    cat > init-next-config.js << 'EOL'
// Next.js 配置
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true
  },
  typescript: {
    ignoreBuildErrors: true
  },
  output: 'standalone'
};

module.exports = nextConfig;
EOL
else
    echo "2. Next.js配置文件已存在..."
fi

# 构建镜像
echo "3. 构建 Docker 镜像..."
echo "   这可能需要几分钟时间，请耐心等待..."
docker compose -f docker-compose.prod.yml build --no-cache

# 检查构建是否成功
if [ $? -ne 0 ]; then
    echo "构建失败，请检查错误信息"
    exit 1
fi

# 启动服务
echo "4. 启动服务..."
docker compose -f docker-compose.prod.yml up -d

# 检查服务状态
echo "5. 检查服务状态..."
sleep 5
docker compose -f docker-compose.prod.yml ps

echo "===== 部署完成 ====="
echo "前端地址: http://localhost"
echo "后端API地址: http://localhost/api"
echo "要查看完整日志，请运行: docker compose -f docker-compose.prod.yml logs -f" 