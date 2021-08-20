import os
import logging
from PIL import Image
from twocaptcha import TwoCaptcha

# логирование
logging.getLogger('selenium').setLevel('CRITICAL')
logging.getLogger('urllib3').setLevel('CRITICAL')
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# настройки автоматического решения капчи
api_key = os.getenv('APIKEY_2CAPTCHA')
solver = TwoCaptcha(api_key)


def solve_mailru_captcha(driver, login):
    captcha_folder_path = 'screenshots/captcha/'
    if not os.path.exists(captcha_folder_path):
        os.mkdir(captcha_folder_path)
    screenshot_path_and_name = f'{captcha_folder_path}{login}.png'

    logger.info('Попали на капчу mail.ru')
    driver.save_screenshot(screenshot_path_and_name)  # делаем скриншот окна браузера
    img = Image.open(screenshot_path_and_name)  # открываем скриншот через Pillow
    area = (38, 168, 264, 245)
    cropped_img = img.crop(area)
    cropped_img.save(screenshot_path_and_name)  # вырезаем кусочек с капчей и сохраняем обратно на диск
    try:
        response_solver: dict = solver.normal(screenshot_path_and_name)
    except Exception as e:
        logger.error(f'Какая-то ошибка в модуле решения капчи: {e}')
        raise
    finally:
        if os.path.exists(screenshot_path_and_name):
            os.remove(screenshot_path_and_name)
    captcha_code = response_solver['code']
    captcha_field = driver.find_element_by_name('captcha_input')
    captcha_field.click()
    captcha_field.send_keys(captcha_code)
    ok_button = driver.find_element_by_id('validate_form_submit')
    ok_button.click()
    logger.info('Успешно решили капчу mail.ru')
    return True
