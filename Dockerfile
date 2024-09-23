FROM python:3.9-slim

# 设置工作目录
WORKDIR /var/deploy

# 复制当前目录内容到工作目录
COPY . /var/deploy

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用运行的端口
EXPOSE 5000

# 设置环境变量
#ENV FLASK_APP=deploy_api.py
#ENV FLASK_RUN_HOST=0.0.0.0

# 运行应用
CMD ["gunicorn", "-c", "gunicorn_config.py", "deploy_api:app"]