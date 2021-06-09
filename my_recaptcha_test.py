# import sys
# import os
# from twocaptcha import TwoCaptcha
# from selenium import webdriver
#
# sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
#
# api_key = os.getenv('APIKEY_2CAPTCHA')


import os
import time

import requests
from selenium import webdriver




class AccountRegister:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.driver = webdriver.Chrome()
        self.api_key = os.getenv('APIKEY_2CAPTCHA')
        self.data_sitekey = '6Lc0CjsUAAAAANK9Z3pR1xlNQxMhbk8ZoYv1ceV5'
        self.url = 'https://pw.mail.ru/'

    def delay(self):
        self.driver.implicitly_wait(5)

    def recaptcha_solver(self):
        self.delay()
        u1 = f"https://rucaptcha.com/in.php?key={self.api_key}&method=userrecaptcha&googlekey={self.data_sitekey}&" \
             f"pageurl={self.url}&json=1&invisible=1"
        r1 = requests.get(u1)
        print(r1.json())
        rid = r1.json().get("request")
        u2 = f"https://rucaptcha.com/res.php?key={self.api_key}&action=get&id={int(rid)}&json=1"
        time.sleep(5)
        while True:
            r2 = requests.get(u2)
            print(r2.json())
            if r2.json().get("status") == 1:
                form_token = r2.json().get("request")
                break
            time.sleep(5)
        print(form_token)
        write_token_js = f'document.getElementById("g-recaptcha-response").innerHTML="{form_token}";'
        self.driver.execute_script(write_token_js)


    def login_to_account(self):
        self.driver.get(self.url)
        self.delay()
        self.driver.find_element_by_xpath("//div[contains(text(),'Войти')]").click()
        self.delay()
        print(self.driver.window_handles)
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]").click()
        self.delay()
        self.driver.switch_to_window(self.driver.window_handles[0])
        self.driver.find_element_by_xpath("//a[contains(text(),'Создать аккаунт')]").click()

        # две галочки
        self.delay()
        self.driver.find_element_by_xpath("//label[contains(text(),'Я соглашаюсь получать новости, рассылки об акциях ')]").click()
        self.driver.find_element_by_xpath("//body/div[6]/div[2]/div[2]/div[1]/p[2]/label[1]").click()


if __name__ == '__main__':
    account = AccountRegister('vasyHall@yandex.ru', 'hSVJlfQmM$b8q')
    account.recaptcha_solver()
