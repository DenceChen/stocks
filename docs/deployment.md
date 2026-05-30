# 部署文档

本文档介绍 Stocks Investment Analysis System 的本地开发环境搭建和生产部署方法。

## 目录

- [本地开发环境](#本地开发环境)
- [Docker 部署](#docker-部署)
- [环境变量配置](#环境变量配置)
- [生产环境建议](#生产环境建议)

## 本地开发环境

### 系统要求

- Python 3.10 或更高版本
- Node.js 18 或更高版本
- npm 或 yarn
- Git

### 后端设置

#### 1. 克隆仓库

```bash
git clone https://github.com/your-org/stocks.git
cd stocks
```

#### 2. 创建虚拟环境

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

如果遇到 AKShare 安装问题：

```bash
pip install akshare --no-cache-dir
```

#### 4. 配置环境变量

复制示例配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```env
LLM_API_KEY=your_minimax_api_key
LLM_BASE_URL=https://api.minimaxi.com/v1
LLM_MODEL=MiniMax-M2.7-highspeed
```

#### 5. 验证安装

```bash
python -c "from src.config import get_config; print(get_config())"
```

#### 6. 启动后端服务

**开发模式（自动重载）：**

```bash
uvicorn src.api.routes:create_app --reload --host 0.0.0.0 --port 8000
```

**或使用启动脚本：**

```bash
python run_api.py
```

API 文档访问：http://localhost:8000/docs

### 前端设置

#### 1. 进入前端目录

```bash
cd web
```

#### 2. 安装依赖

```bash
npm install
```

或使用 yarn：

```bash
yarn install
```

#### 3. 配置 API 地址

编辑 `web/src/services/api.ts`，确认 API base URL：

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

#### 4. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:5173

### 验证开发环境

1. 访问 http://localhost:8000/docs 测试 API
2. 访问 http://localhost:5173 查看前端界面
3. 在前端界面测试股票查询功能

## Docker 部署

### 构建 Docker 镜像

```bash
docker build -t stocks-analysis:latest .
```

### 运行容器

```bash
docker run -d \
  --name stocks-api \
  -p 8000:8000 \
  --env-file .env \
  stocks-analysis:latest
```

### Docker Compose（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_BASE_URL=${LLM_BASE_URL}
      - LLM_MODEL=${LLM_MODEL}
    volumes:
      - ./data:/app/data
      - ./results:/app/results
      - ./logs:/app/logs
    restart: unless-stopped

  web:
    image: node:18-alpine
    working_dir: /app
    ports:
      - "5173:5173"
    command: sh -c "npm install && npm run dev"
    volumes:
      - ./web:/app
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - api
```

启动：

```bash
docker-compose up -d
```

### 生产环境 Docker 部署

对于生产环境，建议：

1. 使用多阶段构建优化镜像大小
2. 使用 nginx 托管前端静态文件
3. 配置健康检查
4. 使用 secrets 管理敏感信息

示例生产 Dockerfile：

```dockerfile
# 后端多阶段构建
FROM python:3.10-slim as backend

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p results logs

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "src.api.routes:create_app", "--host", "0.0.0.0", "--port", "8000"]

# 前端构建
FROM node:18-alpine as frontend-builder

WORKDIR /app
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# 最终镜像
FROM nginx:alpine

COPY --from=frontend-builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 环境变量配置

### 必需变量

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| LLM_API_KEY | MiniMax API 密钥 | sk-cp-xxxxx |
| LLM_BASE_URL | MiniMax API 地址 | https://api.minimaxi.com/v1 |
| LLM_MODEL | 模型名称 | MiniMax-M2.7-highspeed |

### 可选变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| API_PORT | API 服务端口 | 8000 |
| API_HOST | API 服务地址 | 0.0.0.0 |
| LOG_LEVEL | 日志级别 | INFO |
| MAX_TOKENS | LLM 最大 token 数 | 8192 |
| TEMPERATURE | LLM 温度参数 | 0.7 |

### 前端环境变量

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| VITE_API_URL | 后端 API 地址 | http://localhost:8000 |

## 生产环境建议

### 1. 反向代理

使用 nginx 作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/stocks/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 进程管理

使用 systemd 或 supervisor 管理后端服务：

```ini
[Unit]
Description=Stocks API Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/stocks
Environment="PATH=/var/www/stocks/venv/bin"
ExecStart=/var/www/stocks/venv/bin/uvicorn src.api.routes:create_app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. 日志管理

配置日志轮转（logrotate）：

```
/var/www/stocks/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### 4. 监控与健康检查

定期检查服务健康状态：

```bash
curl http://localhost:8000/api/v1/health
```

配置监控告警（如 Prometheus + Grafana）。

### 5. 安全建议

- 使用 HTTPS（Let's Encrypt）
- 限制 CORS 来源
- 实现 JWT 认证
- 设置请求频率限制
- 定期更新依赖包
- 使用 secrets 管理敏感信息
- 配置防火墙规则
