# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /code

# AWSのデフォルトリージョンを設定
ENV AWS_DEFAULT_REGION ap-northeast-1

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 50505

ENTRYPOINT [ "gunicorn", "app:app" ]
# ca61932904ffacr
