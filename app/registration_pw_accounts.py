import logging
import os
import random
import string
import time
from sys import platform

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException, \
    SessionNotCreatedException, TimeoutException, InvalidSelectorException
from selenium.webdriver import DesiredCapabilities
from urllib3.exceptions import MaxRetryError, NewConnectionError

from captcha_solver import solve_mailru_captcha
from proxy import proxy_dict, current_proxy_status, get_good_proxy, redis_block_proxy

# логирование
logging.getLogger('selenium').setLevel('CRITICAL')
logging.getLogger('urllib3').setLevel('CRITICAL')
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# параметры запуска Selenium
DOCKER = os.getenv('DOCKER')
if DOCKER:
    time.sleep(3)  # время на запуск Selenium
else:
    if platform == 'win32':
        CHROME_PATH = os.path.abspath(os.getcwd()) + '\\chromedriver.exe'
    elif platform == 'linux':
        CHROME_PATH = os.path.abspath(os.getcwd()) + '/chromedriver'

DEBUG_SCREENSHOTS = os.getenv('DEBUG_SCREENSHOTS')
if DEBUG_SCREENSHOTS and DEBUG_SCREENSHOTS.lower() in {'1', 'true'}:
    DEBUG_SCREENSHOTS = True
else:
    DEBUG_SCREENSHOTS = False


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
        self.login = account_login.lower()
        self.password = account_password
        self.proxy = account_proxy
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--headless')
        self.options.add_argument(f'--proxy-server={self.proxy}')
        self.pw_main_page_url = 'https://pw.mail.ru/'
        self.driver = self._get_selenium_webdriver()

    def register_account(self):
        try:
            self._open_pw_main_page()
            if self._check_captcha():
                solve_mailru_captcha(self.driver, self.login)
            self._click_main_register_button()
            self._switch_to_window(1)
            self._enter_login_and_password()
            time.sleep(1)
            self._press_mygames_registration_button()
            self._check_has_error()
            self._press_continue_button()
            self._switch_to_window(0)
            time.sleep(3)
            if self._check_captcha():
                solve_mailru_captcha(self.driver, self.login)
            self._press_final_register_button()
            time.sleep(2)
            if self._check_captcha():
                solve_mailru_captcha(self.driver, self.login)
            self._check_registration_status()
            return True
        except Exception:
            return False

    def delay(self, wait_time=10):
        self.driver.implicitly_wait(wait_time)

    def save_debug_screenshot_if_enabled(self, error_short_description='error'):
        if not DEBUG_SCREENSHOTS:
            return False
        screenshots_folder_error = 'screenshots/errors/'
        screenshot_name = f'{error_short_description}-{self.login}.png'

        if not os.path.exists(screenshots_folder_error):
            os.mkdir(screenshots_folder_error)
        self.driver.save_screenshot(screenshots_folder_error + screenshot_name)
        logger.info(f'Скриншот {screenshot_name} сохранён в папку {screenshots_folder_error}')

    def _get_selenium_webdriver(self):
        try:
            if DOCKER:
                driver = webdriver.Remote(command_executor="http://selenium:4444/wd/hub",
                                          desired_capabilities=DesiredCapabilities.CHROME, options=self.options)
            else:
                driver = webdriver.Chrome(executable_path=CHROME_PATH, options=self.options)
            return driver
        except (SessionNotCreatedException, WebDriverException):
            logger.error(f'Не смогли получить webdriver')
            raise
        except (NewConnectionError, MaxRetryError):
            logger.error(f'Selenium не готов')
            time.sleep(1)

    def _check_captcha(self):
        try:
            self.delay(1)
            if self.driver.current_url == 'https://pw.mail.ru/validate/?ref_url=pw.mail.ru':
                return True
            return False
        except WebDriverException:
            logger.error('Браузер упал на проверке URL страницы?')
            raise

    def _open_pw_main_page(self):
        try:
            self.delay()
            self.driver.get(self.pw_main_page_url)
            logger.debug('Открыли главную страницу PW')
        except (WebDriverException, AttributeError):
            logger.error(f'Ошибка в открытии главной страницы PW')
            raise

    def _click_main_register_button(self):
        try:
            self.delay()
            self.driver.find_element_by_xpath("//a[contains(text(),'Регистрация')]").click()
            logger.debug('Нажали кнопку "Регистрация" на главной странице')
        except NoSuchElementException:
            logger.error(f'Отсутствует кнопка "Регистрация" на главной странице')
            self.save_debug_screenshot_if_enabled('missing_registration_button')
            raise

    def _switch_to_window(self, window_index):
        try:
            self.delay()
            self.driver.switch_to.window(self.driver.window_handles[window_index])  # открывается второе окно
            logger.debug(f'Переключились на окно с индексом {window_index}')
        except (IndexError, WebDriverException):
            logger.error(f'Не смогли переключиться на окно с индексом {window_index}')
            raise

    def _enter_login_and_password(self):
        try:
            self.delay()
            self.driver.find_element_by_name('email').send_keys(self.login)
            time.sleep(0.2)
            self.driver.find_element_by_name('password').send_keys(self.password)
            logger.debug(f'Ввели логин и пароль от аккаунта: {self.login} {self.password}')
        except (NoSuchElementException, WebDriverException):
            logger.error(f'Не смогли ввести логин и пароль от аккаунта')
            self.save_debug_screenshot_if_enabled('missing_login_and_password_fields')
            raise

    def _press_mygames_registration_button(self):
        # активируем кнопку "Регистрация"
        self.delay()
        self.driver.execute_script(
            """var button_next = document.getElementsByClassName("ph-form__btn ph-btn gtm_reg_btn");
            for (var i = 0; i < button_next.length; i++) {button_next[i].removeAttribute("disabled");}""")
        time.sleep(0.5)
        logger.debug('Активировали кнопку "Регистрация" в MY.GAMES')
        try:
            self.delay(2)  # Зарегистрироваться
            self.driver.find_element_by_xpath("//button[contains(text(),'Зарегистрироваться')]").click()
            logger.debug('Попробовали нажать кнопку "Зарегистрироваться" в MY.GAMES')
            return True
        except (InvalidSelectorException, NoSuchElementException):
            logger.debug(f'Не смогли нажать на кнопку "Зарегистрироваться" в MY.GAMES')
        try:
            self.delay(2)
            self.driver.find_element_by_xpath("//button[contains(text(),'Регистрация')]").click()  # Регистрация
            logger.debug('Нажали на кнопку "Регистрация" в MY.GAMES')
            return True
        except (InvalidSelectorException, NoSuchElementException):
            logger.error(f'Не смогли нажать на кнопку "Регистрация" в MY.GAMES')
            self.save_debug_screenshot_if_enabled('missing_mygames_registration_button')
            raise

    def _press_continue_button(self):
        try:
            self.delay(5)
            self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]").click()
            logger.debug('Нажали кнопку "Продолжить"')
        except NoSuchElementException:
            try:
                if self.driver.find_element_by_xpath("//div[contains(text(),'Этот email уже занят')]"):
                    logger.warning(f'Почта {self.login} уже занята')
                    raise
            except NoSuchElementException:
                pass
        except StaleElementReferenceException:
            logger.error('Какая-то проблема с кнопкой "Продолжить"')
            self.save_debug_screenshot_if_enabled('missing_continue_button')
            raise

    def _press_final_register_button(self):
        try:
            # активируем кнопку "Зарегистрироваться"
            self.delay()
            self.driver.execute_script("""var elems = document.querySelectorAll(".oauth_modal_button");
                                        [].forEach.call(elems, function(el) {el.classList.remove("disabled");});""")
        except TimeoutException:
            logger.error('Не смогли активировать финальную кнопку "Зарегистрироваться"')
            raise
        try:
            self.delay()
            self.driver.find_element_by_xpath("//div[contains(text(),'Зарегистрироваться')]").click()
            logger.debug('Нажали кнопку финальную кнопку "Зарегистрироваться"')
        except (StaleElementReferenceException, NoSuchElementException):
            logger.error('Не смогли нажать на финальную кнопку "Зарегистрироваться"')
            self.save_debug_screenshot_if_enabled('missing_final_registration_button')
            raise

    def _check_registration_status(self):
        try:
            self.delay()
            self.driver.find_element_by_xpath("//a[contains(text(),'Мой кабинет')]")
            with open('accounts/accounts.txt', 'a') as accounts_file:
                accounts_file.write('\t'.join([self.login, self.password, self.proxy]) + '\n')
            logger.debug(f'Зарегистрировали аккаунт {self.login} и сохранили в базу')
        except NoSuchElementException:
            logger.error(f'Отсутствует кнопка "Мой кабинет"')
            self.save_debug_screenshot_if_enabled('missing_my_cabinet_button')
            raise

    def _check_has_error(self):
        try:
            self.delay(1)
            error_message = self.driver.find_element_by_xpath("//div[@class='ph-alert ph-alert_error']").text
            if error_message == "Превышено число попыток":
                logger.error("Ждём 5 минут, превышено число попыток регистрации")
                time.sleep(300)
                raise
            else:
                logger.critical(f'Новая ошибка: {error_message}')
        except NoSuchElementException:
            logger.debug('Ошибок регистрации нет, идём дальше')

    def __del__(self):
        try:
            self.driver.quit()
            logger.debug(f'Закрыли браузер у аккаунта {self.login}')
        except AttributeError:
            logger.debug(f'Не смогли закрыть браузер у окна {self.login}')


if __name__ == '__main__':
    registration_iterations = 0
    successful_registrations = 0

    while True:
        login, password = account_generator()
        proxy = get_good_proxy()
        account = PwAccount(login, password, proxy)
        if account.register_account():
            successful_registrations += 1
            proxy_dict[proxy]['good_registrations'] += 1
        else:
            proxy_dict[proxy]['bad_registrations'] += 1
            logger.info(f'Аккаунт не зарегистрирован')
            logger.info(current_proxy_status(proxy, proxy_dict))
        del account
        registration_iterations += 1
        logger.info(f'Попыток: {registration_iterations}. Зарегистрировано: {successful_registrations}')
