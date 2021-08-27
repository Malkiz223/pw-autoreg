import logging
import os
import random
import string
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException, \
    SessionNotCreatedException, TimeoutException, InvalidSelectorException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import MaxRetryError, NewConnectionError, ProtocolError

from captcha_solver import solve_mailru_captcha
from config import IN_DOCKER, DEBUG_SCREENSHOTS, CHROMEDRIVER_PATH
from db import save_account
from proxy import get_good_proxy, block_proxy_if_redis_works

# логирование
logger = logging.getLogger(__name__)


def generate_random_account() -> tuple:
    login_list = []
    password_list = []
    for _ in range(random.randint(8, 11)):
        login_list.append(random.choice(string.ascii_lowercase))
    for _ in range(random.randint(9, 13)):
        password_list.append(random.choice(string.ascii_letters + string.digits))
    email_service = random.choice(['@yandex.ru', '@gmail.com', '@ya.ru'])
    login_ = ''.join(login_list) + email_service
    password_ = ''.join(password_list)
    logger.debug(f'Сгенерировали аккаунт: {login_}, {password_}')
    return login_, password_


class PwAccountRegistrar:
    """
    Регистрирует аккаунты по переданным логину и паролю. Может регистрировать с переданными прокси.
    При использовании без контейнера требуется установить Google Chrome версии не ниже, чем у chromedriver.
    На момент написания в репозитории версия 92.0.4515.159.
    Для более стабильной работы с прокси желателен запущенный Redis (будет временно отстранять плохие прокси).
    """

    def __init__(self, account_login: str, account_password: str, account_proxy: str = None):
        self.login = account_login.lower()
        self.password = account_password
        self.options = webdriver.ChromeOptions()
        self.proxy = account_proxy
        if self.proxy:
            self.options.add_argument(f'--proxy-server={self.proxy}')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--headless')
        self.pw_main_page_url = 'https://pw.mail.ru/'
        self.my_games_register_page_url = 'https://account.my.games/oauth2/signup/?continue=https%3A%2F%2Faccount.my.games%2Foauth2%2F%3Fredirect_uri%3Dhttps%253A%252F%252Fpw.mail.ru%252Foauth2.php%253Fcontinue%253D%25252F%26client_id%3Dpw.mail.ru%26response_type%3Dcode%26signup_method%3Demail%252Cphone%26signup_social%3Dmailru%252Cfb%252Cvk%252Cg%252Cok%252Ctwitch%252Ctw%26show_auth_btn%3Dmailru%26lang%3Dru_RU%26gc_id%3D0.61%26signup%3D1&client_id=pw.mail.ru&lang=ru_RU&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Cok%2Ctwitch%2Ctw&show_auth_btn=mailru&gc_id=0.61'
        self.driver = self._get_selenium_webdriver()
        self.set_implicitly_wait()

    def register_account(self) -> bool:
        """
        Основной метод класса. Возвращает false, если в одном из методов произошла ошибка.
        """
        try:
            self._open_my_games_register_page()
            if self._check_captcha():
                solve_mailru_captcha(self.driver, self.login, self.proxy)
            self._enter_login_and_password()
            self._press_mygames_registration_button()
            self._check_has_error()
            self._press_continue_button()
            self.driver.get(self.pw_main_page_url)

            if self._check_captcha():  # если была капча - не залогинит на сайт, надо логиниться самому
                solve_mailru_captcha(self.driver, self.login, self.proxy)
                self.driver.find_element_by_xpath("//div[contains(text(),'Войти')]").click()
                self._switch_to_window_index(1)
                self._press_continue_button()
                self._switch_to_window_index(0)

            self._press_final_register_button()
            if self._check_captcha():
                solve_mailru_captcha(self.driver, self.login, self.proxy)
            return self._check_registration_status()
        except Exception:
            return False

    def set_implicitly_wait(self, wait_time=5) -> None:
        """
        Позволяет не ждать полное время до появления элемента на странице.
        Как только элемент стал активным - возобновляет скрипт.
        При вызове меняет настройку у драйвера, заставляющую не бросать ошибку при отсутствии элемента.
        Вызвав однажды меняет задержку перед исключением на весь скрипт.
        """
        self.driver.implicitly_wait(wait_time)

    def save_debug_screenshot_if_enabled(self, error_short_description='error'):
        """
        Сохраняет скриншот браузера, позволяя выявить причину ошибки. Работает только тогда, когда есть
        os.getenv('DEBUG_SCREENSHOTS'), берётся из config.py.
        """
        if not DEBUG_SCREENSHOTS:
            return False
        screenshots_folder_error = 'screenshots/errors/'
        screenshot_name = f'{error_short_description}-{self.login}.png'

        if not os.path.exists(screenshots_folder_error):
            os.mkdir(screenshots_folder_error)
        self.driver.save_screenshot(screenshots_folder_error + screenshot_name)
        logger.info(f'Скриншот {screenshot_name} сохранён в папку {screenshots_folder_error}')

    def _get_selenium_webdriver(self) -> webdriver:
        """
        Если работает из Docker - пытается запустить удалённый драйвер, предположительно
        запускающийся из docker-compose. В противном случае берёт chromedriver (в зависимости от ОС) из папки.
        Нет смысла выходить из цикла, пока не получен драйвер. options берутся из __init__.
        """
        while True:
            try:
                if IN_DOCKER:
                    driver = webdriver.Remote(command_executor="http://selenium:4444/wd/hub",
                                              desired_capabilities=DesiredCapabilities.CHROME, options=self.options)
                else:
                    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=self.options)
                logger.debug('Получили webdriver')
                return driver
            except (SessionNotCreatedException, WebDriverException, ProtocolError):
                logger.error('Не смогли получить webdriver')
                time.sleep(2)
            except (NewConnectionError, MaxRetryError):
                logger.warning('Selenium не готов')
                time.sleep(2)

    def _check_captcha(self) -> bool:
        """
        Можно переместить модуль в решатель капчи, в любом случае он к нему обращается по итогу.
        """
        try:
            self.set_implicitly_wait(1)
            if self.driver.current_url == 'https://pw.mail.ru/validate/?ref_url=pw.mail.ru':
                return True
            return False
        except WebDriverException:
            logger.error('Браузер упал на проверке URL страницы?')  # ни разу сюда не заходили
            raise
        finally:
            self.set_implicitly_wait()

    def _open_my_games_register_page(self):
        try:
            self.driver.get(self.my_games_register_page_url)
            logger.debug('Открыли главную страницу PW')
        except (WebDriverException, AttributeError):
            logger.error('Ошибка в открытии главной страницы PW')
            raise

    def _switch_to_window_index(self, window_index):
        """
        Во время регистрации аккаунта открывается дополнительное окно, на которое нужно
        переключиться для дальнейшей работы с браузером. Затем вернуться на основное окно.
        """
        try:
            self.driver.switch_to.window(self.driver.window_handles[window_index])  # передаём хендлер нужного окна
            logger.debug(f'Переключились на окно с индексом {window_index}')
        except (IndexError, WebDriverException):
            logger.error(f'Не смогли переключиться на окно с индексом {window_index}')
            raise

    def _enter_login_and_password(self):
        try:
            self.driver.find_element_by_name('email').send_keys(self.login)
            time.sleep(0.2)
            self.driver.find_element_by_name('password').send_keys(self.password)
            logger.debug(f'Ввели логин и пароль от аккаунта: {self.login} {self.password}')
        except (NoSuchElementException, WebDriverException):
            logger.error('Не смогли ввести логин и пароль от аккаунта')
            self.save_debug_screenshot_if_enabled('missing_login_and_password_fields')
            raise

    def _press_mygames_registration_button(self) -> bool:
        """
        Кнопка для регистрации аккаунты зависит от времени, когда аккаунт регистрируется. Как ни парадоксально,
        кнопка меняется примерно раз в две минуты. Либо зависит от прокси, но по наблюдениям и долгому дебаггингу -
        скорее первый вариант. Видимо, особый способ защиты.
        execute_script здесь активирует кнопку для нажатия, позволяя не ставить галочки на всяких согласиях.
        """
        self.driver.execute_script(  # активируем кнопку "Регистрация" или "Зарегистрироваться", они случайны
            """var button_next = document.getElementsByClassName("gtm_reg_btn");
            for (var i = 0; i < button_next.length; i++) {button_next[i].removeAttribute("disabled");}""")
        time.sleep(0.5)
        logger.debug('Активировали кнопку "Регистрация" в MY.GAMES')
        try:
            # ищем текст "егистр", т.к. кнопка случайным образом может называться "Регистрация" и "Зарегистрироваться"
            self.driver.find_element_by_xpath("//button[contains(text(),'егистр')]").click()
            logger.debug('Попробовали нажать кнопку "Зарегистрироваться" в MY.GAMES')
            return True
        except (InvalidSelectorException, NoSuchElementException):
            logger.debug('Не смогли нажать на кнопку "Зарегистрироваться" в MY.GAMES')
            raise

    def _press_continue_button(self):
        try:
            self.set_implicitly_wait(5)
            self.driver.find_element_by_xpath("//button[contains(text(),'Продолжить')]").click()
            logger.debug('Нажали кнопку "Продолжить"')
        except NoSuchElementException:
            try:
                self.set_implicitly_wait(1)
                if self.driver.find_element_by_xpath("//div[contains(text(),'Этот email уже занят')]"):
                    logger.warning(f'Почта {self.login} уже занята')
                    raise
            except NoSuchElementException:
                pass
        except StaleElementReferenceException:
            logger.error('Какая-то проблема с кнопкой "Продолжить"')
            self.save_debug_screenshot_if_enabled('missing_continue_button')
            raise
        finally:
            self.set_implicitly_wait()

    def _press_final_register_button(self):
        """
        Кнопка "Зарегистрироваться", появляющаяся на основной странице уже после регистрации в MY.GAMES.
        Убираем атрибут disabled у кнопки, в результате чего она становится активной (можно не проходить reCaptcha)
        """
        try:
            register_button = WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Зарегистрироваться')]")))
            self.driver.execute_script("""var elems = document.querySelectorAll(".oauth_modal_button");
                                        [].forEach.call(elems, function(el) {el.classList.remove("disabled");});""")
            logger.debug('Активировали кнопку "Зарегистрироваться"')
        except TimeoutException:
            logger.error('Не смогли активировать финальную кнопку "Зарегистрироваться"')
            raise
        try:
            register_button.click()
            logger.debug('Нажали кнопку финальную кнопку "Зарегистрироваться"')
        except (StaleElementReferenceException, NoSuchElementException):
            logger.error('Не смогли нажать на финальную кнопку "Зарегистрироваться"')
            self.save_debug_screenshot_if_enabled('missing_final_registration_button')
            raise

    def _check_registration_status(self) -> bool:
        """
        По завершению регистрации мы должны попасть на главную страницу, где можно понять, зарегистрировались ли мы,
        по наличию кнопки "Мой кабинет".
        """
        try:
            self.set_implicitly_wait(10)
            self.driver.find_element_by_xpath("//a[contains(text(),'Мой кабинет')]")
            save_account(self.login, self.password, self.proxy)
            logger.debug(f'Зарегистрировали аккаунт {self.login} и сохранили в базу')
            return True
        except NoSuchElementException:
            logger.error('Отсутствует кнопка "Мой кабинет"')
            self.save_debug_screenshot_if_enabled('missing_my_cabinet_button')
            return False

    def _check_has_error(self):
        """
        При попытке зарегистрировать аккаунт в MY.GAMES могут быть различные ошибки, не позволяющие
        продолжить регистрацию. На странице появляется поле с текстом ошибки, по тексту анализируем её.
        """
        try:
            self.set_implicitly_wait(1)
            error_message = self.driver.find_element_by_css_selector(".ph-alert_error").text
            if error_message == "Превышено число попыток":
                block_proxy_if_redis_works(self.proxy)
                logger.error(f"Превышено число попыток, блокируем прокси {self.proxy}")
                raise
            else:
                logger.critical(f'Новая ошибка: {error_message}')
        except NoSuchElementException:
            logger.debug('Ошибок регистрации нет, идём дальше')
        finally:
            self.set_implicitly_wait()

    def __del__(self):
        """
        Огромный список исключений из-за удаления инстанса класса после сломанного по различным причинам браузера.
        """
        try:
            self.driver.quit()
            logger.debug(f'Закрыли браузер у аккаунта {self.login}')
        except (AttributeError, ConnectionResetError, ProtocolError,
                SessionNotCreatedException, WebDriverException, MaxRetryError):
            logger.debug(f'Не смогли закрыть браузер у окна {self.login}')


if __name__ == '__main__':
    # счётчики для печати статистики регистраций
    registration_iterations = 0
    successful_registrations = 0

    while True:
        login, password = generate_random_account()
        proxy: str or None = get_good_proxy()  # скрипт успешно отработает с прокси и без него
        account = PwAccountRegistrar(login, password, proxy)
        if account.register_account():
            successful_registrations += 1
        else:
            logger.info('Аккаунт не зарегистрирован')
        registration_iterations += 1
        logger.info(f'Зарегистрировано: {successful_registrations}. Попыток: {registration_iterations}.')
        del account
