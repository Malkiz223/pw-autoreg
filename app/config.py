import logging
import os
from distutils.util import strtobool
from sys import platform

# настройки логирования
LOGGER_LEVEL = os.getenv('LOGGER_LEVEL', 'INFO')
logging.getLogger('selenium').setLevel('CRITICAL')
logging.getLogger('urllib3').setLevel('CRITICAL')
logging.basicConfig(level=LOGGER_LEVEL, format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%H:%M:%S")

# 1, если скрипт запущен в Docker
IN_DOCKER: int = strtobool(os.getenv('DOCKER', 'false'))  # 0 или 1

# будет использоваться chromedriver, если скрипт запущен не в Docker
if platform == 'win32':
    CHROMEDRIVER_PATH = os.path.join(os.path.abspath(os.getcwd()), 'webdriver/chromedriver.exe')
elif platform == 'linux':
    CHROMEDRIVER_PATH = os.path.join(os.path.abspath(os.getcwd()), 'webdriver/chromedriver')

# 1, если нужно сохранять скриншоты ошибок
DEBUG_SCREENSHOTS: int = strtobool(os.getenv('DEBUG_SCREENSHOTS', 'false'))  # 0 или 1

# API решателя капчи от rucaptcha.com или 2captcha.com
CAPTCHA_API_KEY = os.getenv('APIKEY_2CAPTCHA')
