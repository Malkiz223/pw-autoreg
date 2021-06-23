import os
import random
import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, \
    SessionNotCreatedException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from twocaptcha import TwoCaptcha

CHROME_PATH = os.path.abspath(os.getcwd()) + '\\chromedriver.exe'
proxy_list = [
    '194.67.215.166:9434',  # до 5 июля~
    # '194.156.105.232:59704',  # до 15 июня~
    # '45.139.52.130:47490',  # до 15 июня~
    # '45.152.116.197:57991',  # до 15 июня~
    # '45.93.15.181:57875',  # до 15 июня~
    # '45.132.129.171:59146',  # до 15 июня~
    # '193.187.106.207:45124',  # до 15 июня~
    # '45.139.52.19:45854',  # до 15 июня~
    # '109.196.172.207:53402',  # до 15 июня~
    # '45.152.116.126:56394',  # до 15 июня~
    # '31.40.203.35:3000',  # до 11 июля
    # '188.130.143.229:3000',  # до 11 июля
    # '109.248.14.81:3000',  # до 11 июля
    # '188.130.188.121:3000',  # до 11 июля
    # '46.8.22.113:3000',  # до 11 июля
    # '46.8.222.183:3000',  # до 11 июля
    # '188.130.128.170:3000',  # до 11 июля
    # '185.181.244.235:3000',  # до 11 июля
    # '188.130.186.38:3000',  # до 11 июля
    # '46.8.213.90:3000',  # до 11 июля
]


class MailRuObject:
    def __init__(self, account_login, account_password, proxy):
    # def __init__(self, account_login, account_password):
        global proxy_list
        self.login = account_login.lower()
        self.password = account_password
        self.first_name = 'Тамара'
        self.last_name = 'Лазько'
        self.nickname = self.login.split('@')[0]
        # self.proxy = proxy
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        # self.options.add_argument('--headless')
        # self.options.add_argument(f'--proxy-server={self.proxy}')
        self.mail_ru_enter_url = 'https://mail.ru/'
        try:
            # self.driver = webdriver.Chrome(executable_path=CHROME_PATH, options=self.options)
            self.epic_driver = webdriver.Chrome(executable_path=CHROME_PATH, options=self.options)
        except (SessionNotCreatedException, WebDriverException):
            pass

    def delay(self, wait_time=10):
        self.epic_driver.implicitly_wait(wait_time)

    def enter_to_mailru_account(self):
        self.driver.get(self.mail_ru_enter_url)
        self.driver.implicitly_wait(5)
        try:
            login_field = self.driver.find_element_by_xpath(
                "//body/main[@id='grid']/div[@id='grid:middle']/div[1]/div[1]/div[2]/form[1]/div[1]/div[2]/input[1]")
            # login_field = self.driver.find_element_by_xpath("/html[1]/body[1]/main[1]/div[3]/div[1]/div[1]/div[2]/form[1]/div[1]/div[2]/input[1]")
            login_field.click()
            login_field.clear()
            login_field.send_keys(self.login)
            login_field.send_keys(Keys.ENTER)
            time.sleep(3)
            self.driver.implicitly_wait(5)
            password_field = self.driver.find_element_by_xpath(
                "//body/main[@id='grid']/div[@id='grid:middle']/div[1]/div[1]/div[2]/form[1]/div[2]/input[1]")
                # "/html[1]/body[1]/main[1]/div[3]/div[1]/div[1]/div[2]/form[1]/div[2]/input[1]")
            password_field.click()
            password_field.clear()
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.ENTER)
            time.sleep(3)
        except NoSuchElementException:
            return False

    def _get_name_from_mail(self):
        self.driver.get('https://id.mail.ru/profile')
        self.first_name = self.driver.find_element_by_xpath("//input[@id='firstname']").get_attribute('value')
        self.last_name = self.driver.find_element_by_xpath("//input[@id='lastname']").get_attribute('value')
        return self.first_name, self.last_name

    # def _check_verification_code(self):
    #     self.driver.get('https://e.mail.ru/inbox/')
    #     while True:
    #         time.sleep(3)
    #         self.delay()
    #         mails_text = self.driver.find_element_by_xpath("//body/div[@id='app-canvas']").text
    #         if "Email Verification Code: " in mails_text:
    #             for line in mails_text.split('\n'):
    #                 if "Email Verification Code: " in line:
    #                     line = line.split(': ')
    #                     code = line[1][:6]
    #                     return code
    #         else:
    #             self.driver.refresh()

    def registration_to_egs(self):
        # self.first_name, self.last_name = self._get_name_from_mail()
        self.epic_driver.get('https://www.epicgames.com/id/register/epic')
        time.sleep(10)
        print('Прошли 10 секунд')
        self.delay(20)
        country = self.epic_driver.find_element_by_xpath("//input[@id='country']")
        country.click()
        country.clear()
        country.send_keys('Russian Federation')
        time.sleep(0.2)
        self.delay(20)
        self.epic_driver.find_element_by_xpath("//input[@id='name']").send_keys(self.first_name)
        time.sleep(0.2)
        self.delay()
        self.epic_driver.find_element_by_xpath("//input[@id='lastName']").send_keys(self.last_name)
        time.sleep(0.2)
        self.delay()
        self.epic_driver.find_element_by_xpath("//input[@id='displayName']").send_keys(self.nickname)
        time.sleep(0.2)
        self.delay()
        self.epic_driver.find_element_by_xpath("//input[@id='email']").send_keys(self.login)
        time.sleep(0.2)
        self.delay()
        self.epic_driver.find_element_by_xpath("//input[@id='password']").send_keys(self.password)
        time.sleep(0.2)
        self.delay()
        self.epic_driver.find_element_by_xpath("//input[@id='tos']").click()
        time.sleep(0.2)
        self.delay()
        self.epic_driver.find_element_by_xpath("//body/div[2]/div[2]/div[1]/div[1]/div[1]/form[1]/div[7]").click()
        time.sleep(0.2)
        self.delay()

        #################################################

        # api_key = os.getenv('APIKEY_2CAPTCHA')
        #
        # solver = TwoCaptcha(api_key)
        #
        # while True:
        #     try:
        #         result = solver.hcaptcha(
        #             sitekey='b364b1fd-e3d8-4d24-8c41-77a19604b00d',
        #             url='https://www.epicgames.com/id/register/epic',
        #             # proxy={'type': 'HTTPS', 'uri': 'GoNqqm:5cA7Eq@194.67.215.166:9434'}
        #         )
        #         result = result['code']
        #         print(result)
        #         break
        #     except Exception as e:
        #         print(e)
        #         result = ''
        #
        # time.sleep(5)
        # h_captcha_string = '''
        #     var h = document.getElementsByName("h-captcha-response");
        #     for (var i = 0; i < h.length; i++) {h[i].innerHTML="%s"};
        #     ''' % result
        # g_captcha_string = '''
        #     var g = document.getElementsByName("g-recaptcha-response");
        #     for (var i = 0; i < g.length; i++) {g[i].innerHTML="%s"};
        # #     ''' % result

        # document.querySelector('#btn-submit').click()

        # self.delay(1)
        # self.epic_driver.execute_script(h_captcha_string)
        # time.sleep(0.2)
        # self.delay(1)
        # self.epic_driver.execute_script(g_captcha_string)
        # print('Ввели, давай тыкай Регать')
        ######################################################

        # code = self._check_verification_code()
        # code_field = self.epic_driver.find_element_by_xpath(
        #     "//body/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/input[1]")
        # time.sleep(0.2)
        # self.delay()
        # code_field.send_keys(code)


if __name__ == '__main__':
    login = 'toma.lazko.73@bk.ru'
    password = '95CLLUjQW33'
    mail_account = MailRuObject(login, password, random.choice(proxy_list))
    # mail_account.enter_to_mailru_account()
    mail_account.registration_to_egs()

'b364b1fd-e3d8-4d24-8c41-77a19604b00d'
