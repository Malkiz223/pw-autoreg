import logging
import os

from PIL import Image
from twocaptcha import TwoCaptcha

from config import CAPTCHA_API_KEY
from proxy import block_proxy_if_redis_works

# логирование
logger = logging.getLogger(__name__)

# экземпляр автоматического решателя капчи
captcha_solver = TwoCaptcha(CAPTCHA_API_KEY)


def solve_mailru_captcha(driver, login, proxy) -> bool:
    """
    Попадаем сюда, если url страницы совпадает с url капчи. Скриним браузер, вырезает из скрина капчу,
    отправляем скрин решателю капчи. Ответ вставляем в поле ввода и жмём ОК.
    """
    captcha_folder_path = 'screenshots/captcha/'
    if not os.path.exists(captcha_folder_path):
        os.mkdir(captcha_folder_path)
    screenshot_path_and_name = f'{captcha_folder_path}{login}.png'

    logger.info('Попали на капчу mail.ru')
    driver.save_screenshot(screenshot_path_and_name)  # делаем скриншот окна браузера
    full_page_image = Image.open(screenshot_path_and_name)  # открываем скриншот через Pillow
    captcha_area = (38, 168, 264, 245)  # левый верхний угол, правый нижний угол капчи относительно скриншота
    cropped_img = full_page_image.crop(captcha_area)  # вырезаем кусочек с капчей из скриншота
    cropped_img.save(screenshot_path_and_name)  # и сохраняем на диск с тем же именем (заменяя старый скрин)
    try:
        response_solver: dict = captcha_solver.normal(screenshot_path_and_name)
    except Exception as e:
        logger.error(f'Ошибка решения капчи: {e}')
        block_proxy_if_redis_works(proxy, 600)
        logger.debug(f'Заблокировали {proxy} на 10 минут')
        raise
    finally:
        if os.path.exists(screenshot_path_and_name):
            os.remove(screenshot_path_and_name)
    captcha_code = response_solver['code']
    captcha_field = driver.find_element_by_name('captcha_input')
    captcha_field.send_keys(captcha_code)
    ok_button = driver.find_element_by_id('validate_form_submit')
    ok_button.click()
    logger.info('Успешно решили капчу mail.ru')
    return True
