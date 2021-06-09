import csv
import time

import os
import time

import requests

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys

PW_URL = 'https://pw.mail.ru/'
PW_PROMO_URL = 'https://pw.mail.ru/pin.php'
CHROME_WEBDRIVER_PATH = r'C:\Users\User\PycharmProjects\selenium-parser\chromedriver.exe'


class PwAccount:
    def __init__(self, account_login, account_password):
        self.user_agent = UserAgent()
        # options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f'user-agent={self.user_agent.random}')
        self.options.add_argument('--proxy-server=194.67.215.166:9434')
        self.login = account_login
        self.password = account_password
        self.driver = webdriver.Chrome(executable_path=CHROME_WEBDRIVER_PATH,
                                       options=self.options)
        self.api_key = os.getenv('APIKEY_2CAPTCHA')
        self.data_sitekey = '6Lc0CjsUAAAAANK9Z3pR1xlNQxMhbk8ZoYv1ceV5'
        self.page_url = 'https://pw.mail.ru/'

    def login_to_pw_site(self):
        self.driver.get(PW_URL)  # открываем сайт ПВ в Chrome
        self.driver.find_element_by_class_name('enter').click()  # тыкаем Войти
        self._login_second_window()

    def _login_second_window(self):
        while True:
            try:
                self.driver.switch_to.window(self.driver.window_handles[1])  # переключаемся на второе
                break
            except Exception as e:
                print(f'Ждём, пока откроется второе окно, {e}')

        while True:  # вводим логин и ждём, пока поле "Пароль" пропадёт
            try:
                self.driver.implicitly_wait(10)
                self.driver.launch_app()
                login_field = self.driver.find_elements_by_tag_name('input')[0]
                login_field.send_keys(self.login)
                password_field = self.driver.find_elements_by_tag_name('input')[1]
                password_field.send_keys(self.password)
                time.sleep(5)
                password_field.send_keys(Keys.ENTER)
                break
            except NoSuchElementException:
                pass
            except IndexError:
                print('Ищу индексы инпута')

        if 'yandex.ru' not in self.login:
            self._login_third_window()  # третье окно закрыто, продолжаем
            self.driver.implicitly_wait(10)

        # time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[1])
        try:
            checkbox = self.driver.find_element_by_xpath(
                "//body/div[2]/div[1]/div[1]/form[1]/div[2]/div[2]/div[1]/div[2]/label[1]")
            checkbox.click()
            while True:
                try:
                    continue_button = self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]")
                    continue_button.click()
                    self.driver.implicitly_wait(10)
                    # time.sleep(1)
                    break
                except ElementClickInterceptedException:
                    pass
        except NoSuchElementException:
            pass
        while True:
            try:
                continue_button = self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]")
                continue_button.click()
                self.driver.implicitly_wait(10)
                # time.sleep(2)
                break
            except ElementClickInterceptedException:
                pass
            except NoSuchElementException:
                pass
        self.driver.implicitly_wait(10)
        # time.sleep(2)
        try:
            self.driver.switch_to.window(self.driver.window_handles[0])
            checkbox = self.driver.find_element_by_xpath("//body/div[7]/div[2]/div[2]/div[1]/p[2]/label[1]")
            checkbox.click()
            continue_button = self.driver.find_element_by_xpath("//div[contains(text(),'Продолжить')]")
            continue_button.click()
        except ElementClickInterceptedException:
            pass
        except NoSuchElementException:
            pass
        self.driver.implicitly_wait(10)
        # time.sleep(0.5)

    def _login_third_window(self):
        self._third_switch_to_window()
        self._third_enter_the_password_and_press_login()
        self._third_press_allow_button()
        self._third_wait_window_close()

    def _third_switch_to_window(self):
        while True:
            try:
                self.driver.switch_to.window(self.driver.window_handles[2])
                break
            except Exception as e:
                print(f'Ждём третье окно, {e}')

    def _third_enter_the_password_and_press_login(self):
        while True:
            try:
                password_field = self.driver.find_element_by_xpath("//input[@name='password']")
                password_field.click()
                password_field.clear()
                password_field.send_keys(self.password)
                break
            except NoSuchElementException:
                pass
        enter_button = self.driver.find_element_by_xpath(
            "//body/div[@id='login-content']/div[@id='root']"
            "/div[1]/div[2]/div[1]/div[1]/div[1]/form[1]/div[2]/div[1]/div[3]/div[1]/div[1]/button[1]")
        enter_button.click()

    def _third_press_allow_button(self):
        while True:
            if len(self.driver.window_handles) >= 3:  # окно не закрылось после нажатия на Войти
                self.driver.implicitly_wait(10)
                # time.sleep(1)
                try:
                    ok_button = self.driver.find_element_by_xpath(
                        "//body/div[@id='root']/div[1]/div[2]/div[3]/div[3]/div[1]/button[1]")
                    ok_button.click()
                    self.driver.implicitly_wait(10)
                    # time.sleep(2)
                    break
                except NoSuchWindowException:
                    pass
                except AttributeError:
                    pass
                except NoSuchElementException:
                    print('Что-то пошло не так')
            else:
                break

    def _third_wait_window_close(self):
        while True:
            if len(self.driver.window_handles) >= 3:
                print('Окно почему-то не закрылось, жду закрытия окна')
                self.driver.implicitly_wait(10)
                # time.sleep(1)
            else:
                break

    def activate_promo(self, codes):
        for code in codes:
            self.driver.get(PW_PROMO_URL)
            promo_input_field = self.driver.find_element_by_xpath("//input[@id='pin']")
            promo_input_field.click()
            promo_input_field.send_keys(code)
            activate_button = self.driver.find_element_by_xpath(
                "//tbody/tr[1]/td[1]/div[1]/div[2]/div[3]/form[1]/div[2]/input[1]")
            activate_button.click()

    def finish_register(self):
        print('Завершаю регистрацию, жду')
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_xpath("//label[contains(text(),'Я соглашаюсь получать новости, рассылки об акциях ')]").click()
        self.driver.find_element_by_xpath("//body/div[6]/div[2]/div[2]/div[1]/p[2]/label[1]").click()

    def recaptcha_solver(self):
        u1 = f"https://rucaptcha.com/in.php?key={self.api_key}&method=userrecaptcha&googlekey={self.data_sitekey}&pageurl={self.page_url}&json=1&invisible=1"
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
        time.sleep(3)

    def __del__(self):
        print(f'Закрываю аккаунт {self.login}')
        # self.driver.quit()


if __name__ == '__main__':
    with open('accounts.csv', newline='') as file:
        accounts = csv.reader(file, delimiter=';')
        for login, password in accounts:
            print(f'Захожу на {login}')
            account = PwAccount(login, password)
            account.login_to_pw_site()
            account.finish_register()
            account.recaptcha_solver()
            time.sleep(1000)
