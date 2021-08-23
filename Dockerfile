FROM python:slim-buster

WORKDIR /app

COPY /app/requirements.txt .

RUN apt update \
    && apt upgrade \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY /app .

ENTRYPOINT [ "python3", "registration_pw_accounts.py" ]