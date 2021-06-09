import time

import requests
from selenium import webdriver

# API_KEY = "dc9d396bebe4d66315dc925fdede8d71"
data_sitekey = '6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'
page_url = 'https://www.google.com/recaptcha/api2/demo'


def recaptcha_solver():
    driver = webdriver.Chrome()
    driver.get(page_url)
    u1 = f"https://rucaptcha.com/in.php?key={API_KEY}&method=userrecaptcha&googlekey={data_sitekey}&pageurl={page_url}&json=1&invisible=1"
    r1 = requests.get(u1)
    print(r1.json())
    rid = r1.json().get("request")
    u2 = f"https://rucaptcha.com/res.php?key={API_KEY}&action=get&id={int(rid)}&json=1"
    time.sleep(5)
    while True:
        r2 = requests.get(u2)
        print(r2.json())
        if r2.json().get("status") == 1:
            form_token = r2.json().get("request")
            break
        time.sleep(5)
    write_token_js = f'document.getElementById("g-recaptcha-response").innerHTML="{form_token}";'
    submit_js = 'document.getElementById("recaptcha-demo-form").submit();'
    driver.execute_script(write_token_js)
    time.sleep(3)
    driver.execute_script(submit_js)
    time.sleep(10)


if __name__ == '__main__':
    recaptcha_solver()
