import time

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException

url = 'https://porofessor.gg/ru/live/na/IIIlllIIIllIIII'
CHROME_WEBDRIVER_PATH = r'C:\Users\User\PycharmProjects\selenium-parser\chromedriver.exe'

user_agent = UserAgent()
# options
options = webdriver.ChromeOptions()
# options.add_argument(f'user-agent={user_agent.random}')
options.add_argument('--proxy-server=194.67.215.166:9434')
# options.add_argument("--headless")


# options.add_argument('headless')
# options.add_argument('--window-size=1920x1080')
# options.add_argument("--disable-gpu")

# browser
driver = webdriver.Chrome(executable_path=CHROME_WEBDRIVER_PATH, options=options)
# driver.set_window_position(-10000, 0)

driver.get(url)
print(driver.title)

try:
    if driver.find_element_by_xpath("//a[contains(text(),'IIIlllIIIllIIII')]"):
        print('Играет')
except NoSuchElementException:
    print('Не играет')
