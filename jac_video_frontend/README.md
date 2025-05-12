# JAC Video - AI视频生成工具

JAC Video 是一个专注于日语教学视频生成的 AI 工具平台，能够自动生成优质的日语词汇教学视频内容。
![alt text](image.png)
### 日语词汇学习视频
<video width="560" height="315" controls>
  <source src="https://wanjiasu.gitee.io/jac_video_frontend/japanese_vocab_1737699005352.mp4" type="video/mp4">
  您的浏览器不支持视频播放。
</video>
## 🌟 主要功能

- 🎯 日语词汇视频生成：自动生成日语词汇教学短视频
- 🔊 AI 配音：支持日语和中文的专业 AI 配音
- 📝 智能字幕：自动生成双语字幕
- 🎨 动态效果：专业的视觉动画效果

## 🚀 快速部署指南

### 环境要求

- Node.js >= 18.17.0
- npm >= 9.0.0
- Git

### 本地开发部署

1. **克隆项目**
```bash
git clone git@gitee.com:wanjiasu/jac_video_frontend.git
cd jac_video_frontend
```

2. **安装依赖**
```bash
npm install
```
如果安装速度太慢, 可以尝试使用淘宝镜像源
```bash
npm install --registry=https://registry.npmmirror.com
```

3. **环境变量配置**
创建 `.env.local` 文件：
```bash
cp .env.example .env.local
```
```bash
# Supabase配置
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# 本地内网/公网IP配置
NEXT_PUBLIC_API_BASE_URL=your_api_base_url

# 其他配置
NODE_ENV=development 
```

4. **启动开发服务器**
```bash
npm run dev
```

访问 http://localhost:3000 即可看到应用界面

### 生产环境部署

#### 方法一：使用 PM2 部署（推荐）

1. **安装 PM2**
```bash
npm install -g pm2
```

2. **构建项目**
```bash
npm run build
```

3. **创建 PM2 配置文件 `ecosystem.config.js`**
```javascript
module.exports = {
  apps: [{
    name: "jac-video-frontend",
    script: "npm",
    args: "start",
    env: {
      NODE_ENV: "production",
      PORT: 3000
    }
  }]
}
```

4. **启动服务**
```bash
pm2 start ecosystem.config.js
```

#### 方法二：使用 Docker 部署

1. **构建 Docker 镜像**
```bash
docker build -t jac-video-frontend .
```

2. **运行容器**
```bash
docker run -d -p 3000:3000 jac-video-frontend
```

## 📁 项目结构

```
src/
├── app/                    # 页面文件
│   ├── products/          # 产品相关页面
│   │   └── japanese-vocab # 日语词汇功能
├── components/            # 通用组件
│   ├── ui/               # UI组件
│   └── business/         # 业务组件
├── lib/                  # 工具库
└── types/                # 类型定义
```

## 🔧 常见问题解决

### 1. 部署后接口访问问题
- 确保 `.env.local` 中的 `NEXT_PUBLIC_API_URL` 配置正确
- 检查后端服务是否正常运行
- 确认网络和防火墙配置

### 2. 构建失败
```bash
# 清理缓存和依赖
rm -rf .next
rm -rf node_modules
npm cache clean --force

# 重新安装和构建
npm install
npm run build
```

### 3. 性能优化建议
- 使用 nginx 做反向代理
- 配置适当的缓存策略
- 开启 gzip 压缩

## 📝 开发注意事项

1. **代码提交规范**
```bash
git add .
git commit -m "feat(module): your message"
git push
```

2. **分支管理**
- main: 生产环境分支
- develop: 开发环境分支
- feature/*: 功能分支

## 🤝 技术支持

- 问题反馈：[GitHub Issues](your-issues-url)
- 邮件支持：[your-email@example.com]

## 📜 许可证

[MIT License](LICENSE)

## 🙏 致谢

- [Next.js](https://nextjs.org/)
- [TailwindCSS](https://tailwindcss.com/)
- [Shadcn/ui](https://ui.shadcn.com/)

