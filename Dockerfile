# 使用 Python 3.12 官方镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt update && apt install -y build-essential

# 复制项目依赖文件
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . /app/

# 明确复制 env_config 文件夹（包含环境配置文件）
COPY env_config /app/env_config

# 设置环境变量目录（如果需要）
ENV ENV_CONFIG_DIR=/app/env_config

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]


