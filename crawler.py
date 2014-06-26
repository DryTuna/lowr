from lowr_database import get_database_connection
from url_scraper import update_prices


# Thanks for justforfun and jlargent on stackoverflow for email technique
import smtplib
from email.mime.text import MIMEText


def check_price(item):
    if item[2] < item[3]:
        conn = get_database_connection()
        cur = conn.cursor()
        cur.excecute("SELECT username FROM accounts WHERE user_id=%s",
                     (item[0],))
        user = cur.fetchone()
        username = user[1]
        fromaddr = 'lowr.codefellow@gmail.com'
        toaddr = user[2]
        msg = 'Your item has reached the price you wanted it to!\n'
        msg += str(item[1])
        msg += '\n\nThank you,\nThe lowr team'
        username = 'lowr.codefellow'
        password = 'codefellow'
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()


if __name__ == "__main__":
    conn = get_database_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    while True:
        items = cur.fetchmany(5)
        update_prices(items)

        for item in items:
            cur.execute("UPDATE items SET last_price=%s WHERE user_id=%s",
                        (item[3], item[0]))
            check_price(item)

        if len(items) < 5:
            break
