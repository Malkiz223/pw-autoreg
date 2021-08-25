import logging
import random
import time

from redis import Redis, exceptions

from config import IN_DOCKER, proxy_list

# логирование
logger = logging.getLogger(__name__)

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
    redis_works = True  # программа может работать и без Redis
except exceptions.ConnectionError:
    logger.warning('Нет подключения к Redis. Он крайне рекомендуется при работе с прокси')
    redis_works = False


def get_good_proxy() -> str or None:
    """
    Выбирается рандомный прокси из листа, проверяется в Redis, если TTL proxy больше нуля - рандомить следующий
    Как только прокси нет в Редисе - отдавать строку IP:порт
    """
    while True:
        if proxy_list:
            proxy = random.choice(proxy_list)
        else:
            return None

        if not redis_works:
            logger.debug(f'Redis не работает, выдаём случайный прокси: {proxy}')
            return proxy

        try:
            current_proxy_ttl = redis.ttl(proxy)  # проверяем, "заблокирован" ли прокси в Редис
        except exceptions.ConnectionError:
            logger.debug('Redis упал? Не можем подключиться к нему')  # global redis_works = False?
            return False
        if not current_proxy_ttl > 0:  # возвращает -2 на отсутствующие и истёкшие TTL
            block_proxy_if_redis_works(proxy, 20)  # запрещаем брать этот прокси другим клиентам на 20 секунд
            logger.debug(f'Выдали отфильтрованный через Redis прокси: {proxy}')
            return proxy
        else:
            logger.debug(f'{proxy} заблокирован на {current_proxy_ttl} секунд, выбираем следующий')
            time.sleep(1)


def block_proxy_if_redis_works(proxy, block_seconds=300) -> bool:
    """
    Позволяет блокировать выдачу конкретного прокси по различным причинам. Примеры использования:
    Если прокси выдаёт капчу, а денег на балансе для её решения нет - блокируем прокси на 10 минут.
    Если прокси выдаёт ошибку "Превышено количество регистраций" - блокируем на 5 минут.
    Если прокси выдан клиенту, то не выдавать этот прокси другим клиентам 10 секунд.
    """
    if not redis_works:
        return False
    try:
        redis.set(name=proxy, value=0, ex=block_seconds)
    except exceptions.ConnectionError:
        logger.debug('Redis упал? Не можем подключиться к нему')  # global redis_works = False?
        return False
    logger.debug(f'Заблокировали прокси {proxy} на {block_seconds} секунд')
    return True
