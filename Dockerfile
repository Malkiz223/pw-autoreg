FROM python:slim-buster

WORKDIR /app

COPY /app/requirements.txt .

RUN apt update  \
    && apt upgrade \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

ENV APIKEY_2CAPTCHA='dc9d396bebe4d66315dc925fdede8d71'
ENV TZ='Europe/Moscow'
ENV LOG_LEVEL='INFO'
ENV DOCKER=1
ENV DEBUG_SCREENSHOTS=0

COPY /app .

ENTRYPOINT ["python3", "registration_pw_accounts.py"]