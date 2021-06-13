import random
import os
import random
import string
import time
from collections import Counter

from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException, \
    SessionNotCreatedException, TimeoutException, ElementClickInterceptedException
from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA')
solver = TwoCaptcha(api_key)
CHROME_PATH = os.path.abspath(os.getcwd()) + '\\chromedriver.exe'
proxy_list = [
    '194.67.215.166:9434',  # до 7 июля~
    '194.156.105.232:59704',  # до 15 июня~
    '45.139.52.130:47490',  # до 15 июня~
    '45.152.116.197:57991',  # до 15 июня~
    '45.93.15.181:57875',  # до 15 июня~
    '45.132.129.171:59146',  # до 15 июня~
    '193.187.106.207:45124',  # до 15 июня~
    '45.139.52.19:45854',  # до 15 июня~
    '109.196.172.207:53402',  # до 15 июня~
    '45.152.116.126:56394',  # до 15 июня~
    '31.40.203.35:3000',  # до 11 июля
    '188.130.143.229:3000',  # до 11 июля
    '109.248.14.81:3000',  # до 11 июля
    '188.130.188.121:3000',  # до 11 июля
    '46.8.22.113:3000',  # до 11 июля
    '46.8.222.183:3000',  # до 11 июля
    '188.130.128.170:3000',  # до 11 июля
    '185.181.244.235:3000',  # до 11 июля
    '188.130.186.38:3000',  # до 11 июля
    '46.8.213.90:3000',  # до 11 июля
    '46.8.15.7:3000',  # до 12 июля
    '109.248.15.161:3000',  # до 12 июля
    '45.90.196.62:3000',  # до 12 июля
    '46.8.16.100:3000',  # до 12 июля
    '188.130.128.106:3000',  # до 12 июля
    '46.8.22.158:3000',  # до 12 июля
    '46.8.14.69:3000',  # до 12 июля
    '46.8.23.123:3000',  # до 12 июля
    '46.8.111.126:3000',  # до 12 июля
    '188.130.211.147:3000',  # до 12 июля
    '188.130.220.166:3000',  # до 12 июля
    '109.248.205.231:3000',  # до 12 июля
    '185.181.247.235:3000',  # до 12 июля
    '46.8.17.247:3000',  # до 12 июля
    '109.248.15.89:3000',  # до 12 июля
    '109.248.204.31:3000',  # до 12 июля
    '46.8.107.164:3000',  # до 12 июля
    '46.8.110.179:3000',  # до 12 июля
    '188.130.129.194:3000',  # до 12 июля
    '188.130.219.35:3000',  # до 12 июля
    '46.8.22.187:3000',  # до 12 июля
    '109.248.14.119:3000',  # до 12 июля
    '95.182.126.34:3000',  # до 12 июля
    '188.130.142.15:3000',  # до 12 июля
    '188.130.142.65:3000',  # до 12 июля
    '188.130.128.174:3000',  # до 12 июля
    '109.248.167.105:3000',  # до 12 июля
    '109.248.129.48:3000',  # до 12 июля
    '109.248.167.21:3000',  # до 12 июля
    '194.35.113.10:3000',  # до 12 июля
]


def account_generator():
    login_list = []
    password_list = []
    for _ in range(random.randint(8, 11)):
        login_list.append(random.choice(string.ascii_lowercase))
    for _ in range(random.randint(9, 13)):
        password_list.append(random.choice(string.ascii_letters + string.digits))
    service = random.choice(['@yandex.ru', '@gmail.com', '@narod.ru', '@ya.ru'])
    result = ''.join(login_list) + service, ''.join(password_list)
    return result


class PwAccount:
    def __init__(self, account_login, account_password, proxy):
        global proxy_list
        self.login = account_login.lower()
        self.password = account_password
        self.proxy = proxy
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--headless')
        self.options.add_argument(f'--proxy-server={self.proxy}')
        self.page_url = 'https://pw.mail.ru/'
        try:
            self.driver = webdriver.Chrome(executable_path=CHROME_PATH, options=self.options)
        except (SessionNotCreatedException, WebDriverException):
            pass

    def delay(self, wait_time=10):
        self.driver.implicitly_wait(wait_time)

    def register_account(self):
        try:
            self.driver.get(self.page_url)
        except (WebDriverException, AttributeError):
            return False
        self.delay()
        if self.driver.current_url == 'https://pw.mail.ru/validate/?ref_url=pw.mail.ru':
            print('Попали на Мэил капчу')
            self.driver.save_screenshot(f'driver_screens/{self.login}.png')

            img = Image.open(f'driver_screens/{self.login}.png')
            area = (38, 168, 264, 245)
            cropped_img = img.crop(area)
            cropped_img.save(f'captcha_screens/{self.login}.png')

            try:
                result = solver.normal(f'captcha_screens/{self.login}.png')
            except Exception as e:
                print(e)
                print('Какая-то ошибка в отправке капчи, хз')
                return False
            else:
                response_to_captcha = result['code']
                print(response_to_captcha)
                result_captcha_field = self.driver.find_element_by_name('captcha_input')
                result_captcha_field.click()
                result_captcha_field.send_keys(response_to_captcha)
                ok_button = self.driver.find_element_by_id('validate_form_submit')
                ok_button.click()
        try:
            self.delay()
            self.driver.find_element_by_xpath("//a[contains(text(),'Регистрация')]").click()
        except NoSuchElementException:
            return False
        self.delay()
        self.driver.switch_to.window(self.driver.window_handles[1])  # открывается второе окно
        try:
            self.delay()
            self.driver.find_element_by_name('email').send_keys(self.login)
            time.sleep(0.2)
            self.driver.find_element_by_name('password').send_keys(self.password)
        except NoSuchElementException:
            return False
        # вводим пароль и активируем кнопку "Далее"
        self.driver.execute_script(
            """var button_next = document.getElementsByClassName("ph-form__btn ph-btn gtm_reg_btn");
            for (var i = 0; i < button_next.length; i++) {button_next[i].removeAttribute("disabled");}"""
        )
        self.delay()
        self.driver.find_element_by_xpath("//body/div[2]/div[1]/div[1]/form[1]/div[2]/div[3]").click()  # Далее
        try:
            self.delay(5)
            self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]").click()
        except NoSuchElementException:
            try:
                if self.driver.find_element_by_xpath("//div[contains(text(),'Этот email уже занят')]"):
                    try:
                        self._try_login_from_register()
                    except ElementClickInterceptedException:
                        return False
            except NoSuchElementException:
                return False
        except StaleElementReferenceException:
            return False
        # зарегистрировались - возвращаемся к первому окну и создаём аккаунт
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)
        # активируем кнопку "Зарегистрироваться"
        self.delay()
        try:
            self.driver.execute_script("""
                            var elems = document.querySelectorAll(".oauth_modal_button");
                            [].forEach.call(elems, function(el) {el.classList.remove("disabled");});""")
        except TimeoutException:
            return False
        self.delay()
        try:
            self.driver.find_element_by_xpath("//div[contains(text(),'Зарегистрироваться')]").click()
        except (StaleElementReferenceException, NoSuchElementException):
            return False
        self.delay()
        try:
            self.driver.find_element_by_xpath("//a[contains(text(),'Мой кабинет')]")
            with open('new_accounts.txt', 'a') as accounts_file:
                accounts_file.write('\t'.join([self.login, self.password, self.proxy]) + '\n')
            return True
        except Exception:
            return False

    def _try_login_from_register(self):
        self.driver.find_element_by_xpath("//h3[contains(text(),'Вход')]").click()
        self.driver.find_element_by_name('email').send_keys(self.login)
        time.sleep(0.2)
        self.driver.find_element_by_name('password').send_keys(self.password)
        self.driver.execute_script(
            """var button_next = document.getElementsByClassName("ph-form__btn ph-btn gtm_reg_btn");
            for (var i = 0; i < button_next.length; i++) {button_next[i].removeAttribute("disabled");}"""
        )
        self.delay()
        self.driver.find_element_by_xpath("//button[contains(text(),'Войти')]").click()
        self.delay()
        self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]").click()

    def __del__(self):
        print(f'[-] закрываю окно {self.login}')
        try:
            self.driver.quit()
        except AttributeError:
            pass


if __name__ == '__main__':
    i = 0
    bad_proxies_counter = Counter()
    while True:
        login, password = account_generator()
        proxy = random.choice(proxy_list)
        account = PwAccount(login, password, proxy)
        if account.register_account():
            print(f'[+] {login} зарегистрирован')
            i += 1
        else:
            bad_proxies_counter[proxy] += 1
            print(f'[-] {login} не зарегистрирован')
            print(bad_proxies_counter.most_common(20))
        del account
        print(f'[INFO] Зарегистрировано {i} аккаунтов')
