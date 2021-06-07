import csv
import time

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException

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
                login_field = self.driver.find_element_by_class_name('ph-form__input')
                login_field.send_keys(self.login)
                break
            except NoSuchElementException:
                pass

        while True:  # поле Пароль пропало, кнопка "Войти" стала активной, жмём на неё
            try:
                enter_button = self.driver.find_element_by_xpath('//button[text()="Войти"]')
                enter_button.click()
                break
            except ElementClickInterceptedException:
                pass

        self._login_third_window()  # третье окно закрыто, продолжаем

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
                    time.sleep(1)
                    break
                except ElementClickInterceptedException:
                    pass
        except NoSuchElementException:
            pass
        while True:
            try:
                continue_button = self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]")
                continue_button.click()
                time.sleep(2)
                break
            except ElementClickInterceptedException:
                pass
            except NoSuchElementException:
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
        except NoSuchElementException:
            pass
        time.sleep(0.5)

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
                time.sleep(1)
                try:
                    ok_button = self.driver.find_element_by_xpath(
                        "//body/div[@id='root']/div[1]/div[2]/div[3]/div[3]/div[1]/button[1]")
                    ok_button.click()
                    time.sleep(2)
                    break
                except NoSuchWindowException:
                    pass
                except AttributeError:
                    pass
            else:
                break

    def _third_wait_window_close(self):
        while True:
            if len(self.driver.window_handles) >= 3:
                print('Окно почему-то не закрылось, жду закрытия окна')
                time.sleep(1)
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

    def __del__(self):
        print(f'Закрываю аккаунт {self.login}')
        self.driver.quit()


if __name__ == '__main__':
    with open('accounts.csv', newline='') as file:
        accounts = csv.reader(file, delimiter='\t')
        for login, password in accounts:
            print(f'Захожу на {login}')
            account = PwAccount(login, password)
            account.login_to_pw_site()
            account.activate_promo(['NEWMODELS2021', 'MYGAMES2BDAY', 'PW13BIRTHDAY'])
            del account
