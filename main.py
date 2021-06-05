import time
from fake_useragent import UserAgent
from selenium import webdriver


user_agent = UserAgent()

# options
options = webdriver.ChromeOptions()

# set user-agent
options.add_argument(f'user-agent={user_agent.random}')

# set proxy
options.add_argument('--proxy-server=192.99.59.97:3128')

url = 'https://porofessor.gg/ru/live/euw/Composites'
url_user_agent = 'https://xn--80agecg4bru4h.xn--p1ai/'
ip_url = 'https://2ip.ru'


CHROME_WEBDRIVER_PATH = r'C:\Users\User\PycharmProjects\selenium-porofessor-parser\chromedriver.exe'

driver = webdriver.Chrome(executable_path=CHROME_WEBDRIVER_PATH,
                          options=options)

try:
    driver.get(ip_url)
    time.sleep(5)
except Exception as e:
    print('Неведомая ошибка')
    print(e)
finally:
    driver.close()
    driver.quit()
