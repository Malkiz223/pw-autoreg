import os
import logging
from PIL import Image
from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA')
solver = TwoCaptcha(api_key)

logging.getLogger('selenium').setLevel('CRITICAL')
logging.getLogger('urllib3').setLevel('CRITICAL')

log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


def solve_mailru_captcha(driver, login):
    logger.info('Попали на капчу mail.ru')
    driver.save_screenshot(f'driver_screens/{login}.png')

    img = Image.open(f'driver_screens/{login}.png')
    area = (38, 168, 264, 245)
    cropped_img = img.crop(area)
    cropped_img.save(f'captcha_screens/{login}.png')

    try:
        result = solver.normal(f'captcha_screens/{login}.png')
    except Exception as e:
        logger.error(f'Какая-то ошибка в модуле решения капчи: {e}')

        return False
    else:
        response_to_captcha = result['code']
        result_captcha_field = driver.find_element_by_name('captcha_input')
        result_captcha_field.click()
        result_captcha_field.send_keys(response_to_captcha)
        ok_button = driver.find_element_by_id('validate_form_submit')
        ok_button.click()
    return True
