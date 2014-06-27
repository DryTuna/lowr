from url_scraper import update_prices

import psycopg2
import os

# Thanks for justforfun and jlargent on stackoverflow for email technique
import smtplib
from email.mime.text import MIMEText

config = {}
g = {'db': None}

database = os.environ.get('DATABASE_URL')

def connect_db():
    """Return a connection to the configured database"""
    return psycopg2.connect(database)


def get_database_connection():
    db = getattr(g, 'db', None)
    if db is None:
        g[db] = db = connect_db()
    return db


def check_price(item, new_price):
    if item[2] < new_price:
        conn = get_database_connection()
        cur = conn.cursor()
        cur.execute("SELECT username, email FROM accounts WHERE id=%s",
                    (item[0],))
        user = cur.fetchone()
        username = user[0]
        fromaddr = 'lowr.codefellow@gmail.com'
        toaddr = user[1]
        msg = 'Your item has reached the price you wanted it to!\n'
        msg += str(item[1])
        msg += '\n\nThank you,\nThe lowr team'
        username = 'lowr.codefellow'
        password = 'codefellows'
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()


if __name__ == "__main__":
    try:
        conn = get_database_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM items")
        while True:
            items = cur.fetchmany(5)
            new_prices = update_prices(items)

            for i in range(len(items)):
                cur.execute("UPDATE items SET last_price=%s WHERE user_id=%s",
                            (new_prices[i], items[i][0]))
                check_price(items[i], new_prices[i])

            if len(items) < 5:
                break
    except Exception as e:
        username = 'lowr.codefellow'
        fromaddr = 'lowr.codefellow@gmail.com'
        toaddr = 'lowr.codefellow@gmail.com'
        msg = 'DATABASE ERROR! \n' + str(e)
        msg += '\n\nCHECK LOG FILES'
        username = 'lowr.codefellow'
        password = 'codefellows'
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()