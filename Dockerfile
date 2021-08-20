FROM python:slim-buster

WORKDIR /app

COPY /app/requirements.txt .

RUN pip install --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt

ENV APIKEY_2CAPTCHA='***REMOVED***'
ENV TZ='Europe/Moscow'
ENV LOG_LEVEL='INFO'
ENV DOCKER=1
ENV DEBUG_SCREENSHOTS=0

COPY /app .

CMD ["python3", "registration_pw_accounts.py"]