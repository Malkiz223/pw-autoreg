FROM python:slim-buster

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt

ENV SELENIUM_URL='http://selenium:4444/wd/hub'
ENV APIKEY_2CAPTCHA='***REMOVED***'
ENV TIME_ZONE='Europe/Moscow'
ENV LOG_LEVEL='INFO'
ENV DOCKER=1

COPY app .
CMD ["python3", "registration_pw_accounts.py"]