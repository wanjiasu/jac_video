# 生产环境部署指南

本文档提供了如何在生产环境中部署 JAC Video 应用的详细步骤。

## 前提条件

- 已安装 Docker 和 Docker Compose
- 如果需要 HTTPS，请准备好 SSL 证书
- 服务器至少 2GB RAM 和 1 vCPU

## 部署步骤

### 1. 克隆代码库

```bash
git clone https://github.com/wanjiasu/jac_video.git
cd jac_video
```

### 2. 配置环境

#### 后端配置

确保 `jac_video_backend/config.py` 中的配置正确。如果没有该文件，可以从示例文件创建：

```bash
cp jac_video_backend/config.py.example jac_video_backend/config.py
```

根据实际需要修改配置文件中的参数，特别是生产环境相关的参数。

#### 前端配置

前端的环境变量已经在 Dockerfile.prod 中配置，无需额外操作。如果需要自定义，可以编辑 `jac_video_frontend/.env.production` 文件。

### 3. HTTPS 配置（可选但推荐）

如果需要启用 HTTPS：

1. 创建 SSL 证书目录：

```bash
mkdir -p nginx/ssl
```

2. 将 SSL 证书文件（cert.pem 和 key.pem）放入 `nginx/ssl` 目录

3. 编辑 `nginx/nginx.conf` 文件，取消 HTTPS 部分的注释，并更新服务器名称：

```
server_name your-domain.com;
```

### 4. 使用部署脚本

我们提供了一个简单的部署脚本，可以一键完成构建和部署：

```bash
# 添加执行权限
chmod +x deploy-prod.sh

# 运行部署脚本
./deploy-prod.sh
```

如果不使用脚本，可以手动执行以下命令：

```bash
# 构建镜像
docker compose -f docker-compose.prod.yml build

# 启动服务
docker compose -f docker-compose.prod.yml up -d
```

### 5. 验证部署

- 前端应用：访问 `http://localhost` 或 `https://your-domain.com`
- 后端 API：访问 `http://localhost/api` 或 `https://your-domain.com/api`

### 6. 查看日志

```bash
# 查看所有服务的日志
docker compose -f docker-compose.prod.yml logs

# 查看特定服务的日志
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs nginx
```

## 网络问题解决方案

如果在构建过程中遇到网络连接问题（如无法下载依赖、字体文件等），可以尝试以下解决方案：

1. **使用DNS配置**：
   - 已在 docker-compose.prod.yml 中配置使用 Google DNS (8.8.8.8, 8.8.4.4)
   - 如果仍有问题，可以尝试使用其他公共DNS

2. **镜像源配置**：
   - 后端使用阿里云镜像源
   - 如果阿里云源不可用，可以尝试其他源（如中科大源）

3. **前端构建问题**：
   - 前端构建配置已修改为忽略 ESLint 和 TypeScript 错误
   - 如果遇到字体下载问题，可以考虑将字体文件下载到本地使用

4. **代理设置**：
   - 如果服务器需要通过代理访问外网，可以在 docker-compose.prod.yml 中添加代理设置：
     ```yaml
     environment:
       - HTTP_PROXY=http://your-proxy:port
       - HTTPS_PROXY=http://your-proxy:port
     ```

## 维护和更新

### 更新应用

当有新版本发布时，可以按照以下步骤更新应用：

```bash
# 拉取最新代码
git pull

# 重新构建服务
docker compose -f docker-compose.prod.yml build

# 重启服务
docker compose -f docker-compose.prod.yml up -d
```

### 备份数据

定期备份重要数据：

```bash
# 备份静态文件
docker cp $(docker compose -f docker-compose.prod.yml ps -q backend):/app/static ./backups/static_$(date +%Y%m%d)
```

## 故障排除

### 常见问题

1. **服务无法启动**
   - 检查日志：`docker compose -f docker-compose.prod.yml logs`
   - 确保端口未被占用

2. **前端无法连接后端**
   - 检查 Nginx 配置
   - 确认环境变量设置正确

3. **静态文件无法访问**
   - 检查 volumes 挂载是否正确
   - 确认文件权限设置

4. **构建失败**
   - 尝试单独构建有问题的服务：`docker compose -f docker-compose.prod.yml build <service_name>`
   - 检查日志，排查具体错误

### 重启服务

```bash
docker compose -f docker-compose.prod.yml restart [service_name]
```

## 安全建议

1. 启用 HTTPS
2. 设置防火墙，只开放必要端口（80、443）
3. 定期更新所有依赖并构建新镜像
4. 如果可能，使用非 root 用户运行容器 