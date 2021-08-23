import logging
import random
import time

from redis import Redis, exceptions

from config import IN_DOCKER, proxy_list

# логирование
logger = logging.getLogger(__name__)

# создание удобного словаря из config.proxy_list
proxy_dict = dict()
for proxy in proxy_list:
    proxy_dict[proxy] = {'good_registrations': 0, 'bad_registrations': 0}

# подключение к Redis
try:
    if IN_DOCKER:
        redis = Redis(host='redis')
        redis.ping()  # если не сделать, то он будет считаться запущенным в любом случае
        logger.info('Подключились к Docker Redis')
    else:
        redis = Redis()
        redis.ping()  # если не сделать, то он будет считаться запущенным в любом случае
        logger.info('Подключились к локальному Redis')
except exceptions.ConnectionError:
    logger.error('Нет подключения к Redis')
    raise


def get_good_proxy():
    """
    Выбирается рандомный прокси из листа, проверяется в Redis, если TTL proxy больше нуля - рандомить следующий
    Как только прокси нет в Редисе - отдавать строку IP:порт
    """
    while True:
        proxy_ = random.choice(proxy_list)
        current_proxy_ttl = redis.ttl(proxy_)  # проверяем, "забанен" ли прокси в Редис
        if not current_proxy_ttl > 0:  # Возвращает -2 на отсутствующие и истёкшие TTL
            redis_block_proxy(proxy_, 10)  # запрещаем брать этот прокси другим клиентам на 10 секунд
            logger.debug(f'Выдали прокси: {proxy_}')
            return proxy_
        else:
            logger.debug(f'{proxy_} заблокирован на {current_proxy_ttl} секунд, выбираем следующий')
            time.sleep(1)


def current_proxy_statistic(proxy: str, proxy_status_dict: dict) -> str:
    """
    Статистика конкретного прокси печатается в консоль, если регистрация аккаунта на данном прокси закончилась провалом.
    Позволяет заметить прокси с околонулевым процентом регистраций, чтобы вручную убрать его из списка.
    """
    proxy_without_port = proxy.split(':')[0]
    good_registrations = proxy_status_dict[proxy]['good_registrations']
    bad_registrations = proxy_status_dict[proxy]['bad_registrations']
    total_registrations = good_registrations + bad_registrations
    success_rate = good_registrations / total_registrations * 100
    # сообщение вида '123.45.67.89:   17/18   [94.44% success]'
    return f'{proxy_without_port}:\t{good_registrations}/{total_registrations}\t[{success_rate:.2f}% success]'


def block_proxy_if_redis_works(proxy, block_seconds=300) -> bool:
    """
    Позволяет блокировать выдачу конкретного прокси по различным причинам. Примеры использования:
    Если прокси выдаёт капчу, а денег на балансе для её решения нет - блокируем прокси на 10 минут.
    Если прокси выдаёт ошибку "Превышено количество регистраций" - блокируем на 5 минут.
    Если прокси выдан клиенту, то не выдавать этот прокси другим клиентам 10 секунд.
    """
    if not redis_works:
        return False
    redis.set(name=proxy, value=0, ex=block_seconds)
    logger.debug(f'Заблокировали прокси {proxy} на {block_seconds} секунд')
    return True
