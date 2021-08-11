import os
import random
import string
import time
from collections import Counter
from sys import platform

import selenium.common.exceptions
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException, \
    SessionNotCreatedException, TimeoutException, ElementClickInterceptedException
from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA')
solver = TwoCaptcha(api_key)

if platform == 'win32':
    CHROME_PATH = os.path.abspath(os.getcwd()) + '\\chromedriver.exe'
elif platform == 'linux':
    CHROME_PATH = os.path.abspath(os.getcwd()) + '/chromedriver'
proxy_list = [
    '185.181.244.105:3000',  # до 9 августа
]


def account_generator():
    login_list = []
    password_list = []
    for _ in range(random.randint(8, 11)):
        login_list.append(random.choice(string.ascii_lowercase))
    for _ in range(random.randint(9, 13)):
        password_list.append(random.choice(string.ascii_letters + string.digits))
    service = random.choice(['@yandex.ru', '@gmail.com', '@ya.ru'])
    result = ''.join(login_list) + service, ''.join(password_list)
    return result


class PwAccount:
    def __init__(self, account_login, account_password, account_proxy):
        global proxy_list
        self.login = account_login.lower()
        self.password = account_password
        self.proxy = account_proxy
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
        print(f'[INFO] Начинаем регистрацию аккаунта {self.login}')
        try:
            self.driver.get(self.page_url)
        except (WebDriverException, AttributeError):
            return False
        self.delay()

        if self.driver.current_url == 'https://pw.mail.ru/validate/?ref_url=pw.mail.ru':
            print('Попали на Мэил капчу')
            self._solve_mailru_captcha()

        try:
            self.delay()
            self.driver.find_element_by_xpath("//a[contains(text(),'Регистрация')]").click()
        except NoSuchElementException:
            return False

        try:
            self.delay()
            self.driver.switch_to.window(self.driver.window_handles[1])  # открывается второе окно
        except IndexError:
            return False

        try:
            self.delay()
            self.driver.find_element_by_name('email').send_keys(self.login)
            time.sleep(0.2)
            self.driver.find_element_by_name('password').send_keys(self.password)
        except (NoSuchElementException, WebDriverException):
            return False

        # вводим пароль и активируем кнопку "Зарегистрироваться"
        self.driver.execute_script(
            """var button_next = document.getElementsByClassName("ph-form__btn ph-btn gtm_reg_btn");
            for (var i = 0; i < button_next.length; i++) {button_next[i].removeAttribute("disabled");}"""
        )
        self.delay()
        try:
            self.driver.find_element_by_xpath(
                "/html/body/div[2]/div/div/div/form/div[1]/div[4]").click()  # Зарегистрироваться
        except selenium.common.exceptions.InvalidSelectorException:
            print('[ERROR] какая-то проблема с кнопкой "Зарегистрироваться"')
            return False

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

        try:
            self.delay()
            self.driver.find_element_by_xpath("//div[contains(text(),'Зарегистрироваться')]").click()
        except (StaleElementReferenceException, NoSuchElementException):
            return False

        try:
            self.delay()
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

    def _solve_mailru_captcha(self):
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
        return True

    def __del__(self):
        print(f'[-] закрываю окно {self.login}')
        try:
            self.driver.quit()
        except AttributeError:
            pass


if __name__ == '__main__':
    accounts_counter = 0
    bad_proxies_counter = Counter()
    while True:
        login, password = account_generator()
        proxy = random.choice(proxy_list)
        account = PwAccount(login, password, proxy)
        if account.register_account():
            print(f'[+] {login} зарегистрирован')
            accounts_counter += 1
        else:
            bad_proxies_counter[proxy] += 1
            print(f'[-] {login} не зарегистрирован')
            print(bad_proxies_counter.most_common(20))
        del account
        print(f'[INFO] Зарегистрировано аккаунтов: {accounts_counter}')
