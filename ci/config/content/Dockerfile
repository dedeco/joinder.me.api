# Dockerfile
FROM python:3.7-slim
WORKDIR /content
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . .
RUN pip install -r src/content/requirements.txt
CMD gunicorn --bind :8080 --workers 5 --threads 8 "src.content.app:app"