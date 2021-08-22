import logging
import os
from sys import platform

# записываем свои прокси в виде 'IP:port'
# логины и пароли пока не поддерживаются, привязываем прокси к своему IP
proxy_list: list[str] = [
    '188.130.142.59:3000',
    '188.130.128.166:3000',
    '46.8.110.154:3000',
    '45.15.73.129:3000',
    '46.8.157.223:3000',
    '185.181.245.239:3000',
    '92.119.193.143:3000',
    '185.181.246.84:3000',
    '5.183.130.165:3000',
    '46.8.192.35:3000',
    '185.181.247.48:3000',
    '109.248.15.66:3000',
    '188.130.129.225:3000',
    '188.130.137.104:3000',
    '94.158.190.15:3000',
    '109.248.139.89:3000',
    '109.248.143.64:3000',
    '46.8.156.135:3000',
    '109.248.14.78:3000',
    '94.158.190.37:3000',
    '46.8.106.103:3000',
    '109.248.143.157:3000',
    '31.40.203.70:3000',
    '46.8.56.215:3000',
    '188.130.128.211:3000',
    '188.130.129.87:3000',
    '45.11.21.4:3000',
    '46.8.110.196:3000',
    '45.87.253.55:3000',
    '188.130.128.17:3000',
    '109.248.205.7:3000',
    '45.87.252.14:3000',
    '185.181.245.172:3000',
    '109.248.129.180:3000',
    '95.182.125.184:3000',
    '109.248.205.222:3000',
    '188.130.136.130:3000',
    '46.8.154.89:3000',
    '188.130.136.3:3000',
    '188.130.189.128:3000',
    '109.248.142.54:3000',
    '109.248.143.4:3000',
    '46.8.157.90:3000',
    '188.130.128.205:3000',
    '185.181.245.27:3000',
    '46.8.107.220:3000',
    '46.8.22.146:3000',
    '188.130.137.226:3000',
    '188.130.129.201:3000',
    '92.119.193.63:3000',
    '95.182.124.142:3000',
    '45.15.73.154:3000',
    '109.248.204.172:3000',
    '45.87.253.149:3000',
    '188.130.189.9:3000',
    '45.81.136.169:3000',
    '188.130.220.157:3000',
    '45.11.21.237:3000',
    '46.8.154.25:3000',
    '109.248.15.227:3000',
    '109.248.204.45:3000',
    '45.15.72.24:3000',
    '109.248.166.109:3000',
    '95.182.124.95:3000',
    '45.84.177.21:3000',
    '46.8.23.137:3000',
    '194.34.248.125:3000',
    '109.248.167.229:3000',
    '185.181.244.43:3000',
    '109.248.128.113:3000',
    '188.130.129.92:3000',
    '109.248.167.226:3000',
    '46.8.106.251:3000',
    '194.35.113.239:3000',
    '109.248.204.25:3000',
    '109.248.205.54:3000',
    '46.8.110.172:3000',
    '109.248.49.121:3000',
    '188.130.142.83:3000',
    '46.8.57.220:3000',
    '46.8.57.205:3000',
    '46.8.23.2:3000',
    '188.130.129.180:3000',
    '188.130.137.164:3000',
    '46.8.22.7:3000',
    '188.130.128.240:3000',
    '188.130.184.77:3000',
    '188.130.129.27:3000',
    '46.8.23.102:3000',
    '109.248.143.248:3000',
    '45.86.0.199:3000',
    '46.8.192.247:3000',
    '188.130.188.109:3000',
    '109.248.204.81:3000',
    '45.87.253.82:3000',
    '188.130.143.234:3000',
    '5.183.130.116:3000',
    '185.181.244.87:3000',
    '185.181.245.195:3000',
    '46.8.222.109:3000',
    '188.130.128.16:3000',
    '188.130.221.106:3000',
    '109.248.128.20:3000',
    '92.119.193.201:3000',
    '109.248.205.196:3000',
    '45.11.20.129:3000',
    '46.8.17.23:3000',
    '45.15.72.163:3000',
    '188.130.220.20:3000',
    '31.40.203.10:3000',
    '185.181.244.105:3000',  # до 8 сентября 8:50
]

# настройки логгера
LOGGER_LEVEL = os.getenv('LOGGER_LEVEL', 'INFO')
logging.getLogger('selenium').setLevel('CRITICAL')
logging.getLogger('urllib3').setLevel('CRITICAL')
logging.basicConfig(level=LOGGER_LEVEL, format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%H:%M:%S")

# True, если скрипт запущен в Docker
IN_DOCKER = True if os.getenv('DOCKER') else False

# будет использоваться, если скрипт запущен не в Docker (тогда использовать свои chromedriver)
if platform == 'win32':
    CHROMEDRIVER_PATH = os.path.abspath(os.getcwd()) + '\\chromedriver.exe'
elif platform == 'linux':
    CHROMEDRIVER_PATH = os.path.abspath(os.getcwd()) + '/chromedriver'

# API решателя капчи от rucaptcha.com
CAPTCHA_API_KEY = os.getenv('APIKEY_2CAPTCHA')

# True, если нужно сохранять скриншоты ошибок
DEBUG_SCREENSHOTS = os.getenv('DEBUG_SCREENSHOTS')
if DEBUG_SCREENSHOTS and DEBUG_SCREENSHOTS.lower() in {'1', 'true'}:
    DEBUG_SCREENSHOTS = True
else:
    DEBUG_SCREENSHOTS = False
