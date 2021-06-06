import sqlite3


def create_users_database():
    conn = sqlite3.connect('funpay.sqlite')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users ('
                '    id INTEGER PRIMARY KEY,'
                '    username VARCHAR(100),'
                '    registration_date VARCHAR(50),'
                '    online_status VARCHAR(50),'
                '    reviews_counter VARCHAR(50),'
                '    added_to_base INTEGER(10))')


if __name__ == '__main__':
    create_users_database()
