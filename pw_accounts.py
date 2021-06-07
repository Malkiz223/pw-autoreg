import time
import csv

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

user_agent = UserAgent()
# options
options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={user_agent.random}')
options.add_argument('--proxy-server=194.67.215.166:9434')

PW_URL = 'https://pw.mail.ru/'
PW_PROMO_URL = 'https://pw.mail.ru/pin.php'
CHROME_WEBDRIVER_PATH = r'C:\Users\User\PycharmProjects\selenium-parser\chromedriver.exe'


class PwAccount:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.driver = webdriver.Chrome(executable_path=CHROME_WEBDRIVER_PATH,
                                       options=options)

    def login_to_pw_site(self):
        self.driver.get(PW_URL)  # открываем сайт ПВ в Chrome
        self.driver.find_element_by_class_name('enter').click()  # тыкаем Войти
        self.driver.switch_to.window(self.driver.window_handles[1])  # переключаемся на новое окно
        while True:
            try:
                login = self.driver.find_element_by_class_name('ph-form__input')
                login.send_keys(self.login)
                break
            except NoSuchElementException:
                pass
        while True:
            try:
                enter_button = self.driver.find_element_by_xpath('//button[text()="Войти"]')
                enter_button.click()
                break
            except ElementClickInterceptedException:
                pass
        self.driver.switch_to.window(self.driver.window_handles[2])
        while True:
            try:
                password = self.driver.find_element_by_xpath("//input[@name='password']")
                password.click()
                password.clear()
                password.send_keys(self.password)
                break
            except NoSuchElementException:
                pass
        enter_button = self.driver.find_element_by_xpath(
            "//body/div[@id='login-content']/div[@id='root']"
            "/div[1]/div[2]/div[1]/div[1]/div[1]/form[1]/div[2]/div[1]/div[3]/div[1]/div[1]/button[1]")
        enter_button.click()

        time.sleep(2)
        if len(self.driver.window_handles) >= 3:
            try:
                ok_button = self.driver.find_element_by_xpath(
                    "//body/div[@id='root']/div[1]/div[2]/div[3]/div[3]/div[1]/button[1]")
                ok_button.click()
            except Exception as e:
                print('Кнопки "Разрешить" нет')

        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[1])
        try:
            checkbox = self.driver.find_element_by_xpath(
                "//body/div[2]/div[1]/div[1]/form[1]/div[2]/div[2]/div[1]/div[2]/label[1]")
            checkbox.click()
            while True:
                try:
                    continue_button = self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]")
                    continue_button.click()
                    break
                except ElementClickInterceptedException:
                    pass
        except Exception:
            pass
        time.sleep(2)
        while True:
            try:
                continue_button = self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]")
                continue_button.click()
                break
            except ElementClickInterceptedException:
                pass
        time.sleep(2)
        try:
            self.driver.switch_to.window(self.driver.window_handles[0])
            checkbox = self.driver.find_element_by_xpath("//body/div[7]/div[2]/div[2]/div[1]/p[2]/label[1]")
            checkbox.click()
            continue_button = self.driver.find_element_by_xpath("//div[contains(text(),'Продолжить')]")
            continue_button.click()
        except ElementClickInterceptedException:
            pass
        time.sleep(0.5)
        print(f'Залогинились в {self.login}')

    def activate_promo(self, codes):
        for code in codes:
            self.driver.get(PW_PROMO_URL)
            promo_input_field = self.driver.find_element_by_xpath("//input[@id='pin']")
            promo_input_field.click()
            promo_input_field.send_keys(code)
            activate_button = self.driver.find_element_by_xpath(
                "//tbody/tr[1]/td[1]/div[1]/div[2]/div[3]/form[1]/div[2]/input[1]")
            activate_button.click()
            time.sleep(2)


with open('accounts.csv', newline='') as file:
    accounts = csv.reader(file, delimiter='\t')
    for login, password in accounts:
        print(login, password)
        account = PwAccount(login, password)
        account.login_to_pw_site()
        account.activate_promo(['NEWMODELS2021', 'MYGAMES2BDAY', 'PW13BIRTHDAY'])
