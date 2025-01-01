FROM python:3.11-slim

WORKDIR /app
COPY gun.py logger_config.py service.py requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/simple/

EXPOSE 5002

CMD ["gunicorn", "-c", "gun.py", "service:app"]