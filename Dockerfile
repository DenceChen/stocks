FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建结果目录
RUN mkdir -p results

# 设置环境变量
ENV PYTHONPATH=/app

# 运行命令
ENTRYPOINT ["python", "-m", "stocks.src.main"] 