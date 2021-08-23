import sqlite3
import time

connect = sqlite3.connect('accounts/accounts.sqlite3')
cursor = connect.cursor()


def _init_accounts_db_if_not_exists() -> None:
    cursor.execute('CREATE TABLE IF NOT EXISTS accounts ('
                   'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'login VARCHAR UNIQUE NOT NULL,'
                   'password VARCHAR NOT NULL,'
                   'proxy VARCHAR,'
                   'creation_time INTEGER)')
    connect.commit()


def save_account(login: str, password: str, proxy: str):
    cursor.execute('INSERT INTO accounts (login, password, proxy, creation_time) VALUES (?, ?, ?, ?)',
                   (login, password, proxy, int(time.time()),))
    connect.commit()


_init_accounts_db_if_not_exists()
