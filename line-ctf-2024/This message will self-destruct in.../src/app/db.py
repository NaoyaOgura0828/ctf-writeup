import mysql.connector
import logging

from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD

logger = logging.getLogger(__name__)

def connect_mysql():
    return mysql.connector.connect(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        database='db'
    )

def init():
    with connect_mysql() as conn:
        with conn.cursor() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS images
                        (id varchar(100) PRIMARY KEY, type varchar(100), password varchar(100))''')
            conn.commit()

def add_image(id, mimetype, password):
    logger.info(f'db.add_image: {id}')
    with connect_mysql() as conn:
        with conn.cursor() as c:
            c.execute('INSERT INTO images VALUES (%s, %s, %s)', (id, mimetype, password))
            conn.commit()

def get_image(id):
    logger.info(f'db.get_image: {id}')
    with connect_mysql() as conn:
        with conn.cursor() as c:
            c.execute('SELECT * FROM images WHERE id=%s', (id,))
            result = c.fetchone()
            conn.close()
            return result

def delete_image(id):
    logger.info(f'db.delete_image: {id}')
    with connect_mysql() as conn:
        with conn.cursor() as c:
            c.execute('DELETE FROM images WHERE id=%s', (id,))
            conn.commit()


if __name__ == "__main__":
    init()