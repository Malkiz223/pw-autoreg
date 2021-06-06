import sqlite3
import time

import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

user_agent = UserAgent()

PROCESS_NUMBER = 5
# TOTAL_FUNPAY_USERS = 3_515_000
TOTAL_FUNPAY_USERS = 300
PARSE_FOR_PROCESS = 10
funpay_user_url = 'https://funpay.ru/users/{}/'
proxy = {'http': 'http://194.67.215.166:9434'}


user_id = (user_id for user_id in range(1, TOTAL_FUNPAY_USERS, PARSE_FOR_PROCESS))


def get_funpay_soup(user_id) -> BeautifulSoup or None:
    url = funpay_user_url.format(user_id)
    headers = {'User-Agent': f'{user_agent.random}'}
    r = requests.get(url, headers=headers, proxies=proxy)
    # r = requests.get(url, headers=headers)
    if 'Страница не найдена' in r.text:
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    for e in soup.find_all('br'):
        e.replace_with(' ')
    return soup


def find_data_from_soup(soup, user_id) -> tuple or None:
    if not soup:
        return None
    try:
        username = soup.select('h1.mb40')[0].text.split()[0]
    except IndexError as e:
        print(e, soup)
    registration_date = soup.find('div', {'class': 'col-sm-4 col-xs-6'}).find('div', {'class': 'text-nowrap'}).text
    registration_date = ' '.join(registration_date.split()[:4])

    online_status = soup.find('span', {'class': 'media-user-status'}) \
        .text.strip() \
        .replace('  ', '') \
        .replace('(', ' (')
    try:
        # отзывов может не быть
        reviews_counter = soup.find('div', {'class': 'text-mini text-light mb5'}).text.split()[0]
    except AttributeError:
        reviews_counter = None
    return user_id, username, registration_date, online_status, reviews_counter


def add_user_info_into_database(user_info):
    conn = sqlite3.connect('funpay.sqlite')
    cursor = conn.cursor()
    user_id, username, registration_date, online_status, reviews_counter = user_info
    current_time = int(time.time())
    cursor.execute('''INSERT OR IGNORE INTO users 
    (id, username, registration_date, online_status, reviews_counter, added_to_base)
     VALUES (?, ?, ?, ?, ?, ?)''',
                   (user_id, username, registration_date, online_status, reviews_counter, current_time), )
    conn.commit()
    conn.close()


def main(start_user_id):
    print(f'Запущен процесс, {start_user_id}')
    for user_id in range(start_user_id, start_user_id + PARSE_FOR_PROCESS):
        soup = get_funpay_soup(user_id)
        data = find_data_from_soup(soup, user_id)
        user_id, username, registration_date, online_status, reviews_counter = data
        add_user_info_into_database(data)
        print(f'Process:\t{start_user_id}: ID:\t{user_id}, name:\t{username}')


if __name__ == '__main__':
    pool = Pool(PROCESS_NUMBER)
    pool.map(main, user_id)
