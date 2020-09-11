# Dockerfile
FROM python:3.7-slim
WORKDIR /profile
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . .
RUN pip install -r src/profile/requirements.txt
CMD gunicorn --bind :8080 --workers 5 --threads 8 "src.profile.app:app"