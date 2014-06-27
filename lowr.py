# -*- coding: utf-8 -*-


#  GENERAL PURPOSE
import os
import datetime

# FLASK RELATED
from flask import Flask
from flask import g
from flask import redirect
from flask import url_for
from flask import session
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import abort

import gevent
import crawler

#  DATABASE RELATED
import psycopg2
from passlib.hash import pbkdf2_sha256
from lowr_database import get_database_connection

# CUSTOM_SCRAPER
from amazon_scraper import search_results as uni_search
from amazon_book_scraper import search_results as book_search


app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template('main.html')


@app.route("/search", methods=['GET', 'POST'])
def search():
    import json
    results = []


    data = json.loads(request.form['data'])
    querey_data = {}
    for item in data:
        if item['name'] == 'search_category':
            querey_data['category'] = item['value']
        if item['name'] == 'search_text':
            querey_data['keywords'] = item['value']
        if item['name'] == 'search_min_price':
            querey_data['price'] = item['value']
        if item['name'] == 'search_price_range':
            querey_data['price_range'] = item['value']

    keywords = querey_data['keywords']
    category = querey_data['category']
    price = querey_data['price']
    price_range = querey_data['price_range']

    if category == 'Books' or \
       category == 'CDs & Vinyl' or \
       category == 'Software' or \
       category == 'Video Games':
        file_ = book_search(keywords, category, price, price_range)
    else:
        file_ = uni_search(keywords, category, price, price_range)

    while True:
        try:
            results.append(file_.pop()._data)
        except IndexError:
            break

    return render_template('search.html', results=results)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            do_login(request.form['login_username'].encode('utf-8'),
                     request.form['login_password'].encode('utf-8'))
        except ValueError:
            error = "Login Failed"
        except TypeError:
            error = "Invalid username/password"
        except Exception:
            return redirect(url_for('home_page'))
        else:
            return redirect(url_for('home_page'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home_page'))



@app.route('/crawl', methods=['GET', 'POST'])
def crawl_on_demand():
    user = session['username']

    conn = get_database_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM accounts WHERE username = %s", [user])
    try:
        id, email = cur.fetchone()
    except Exception as e:
        print e
    user = {
            'username': user,
            'email': email
        }
    crawler.crawl_per_user(id)
    cur = conn.cursor()
    cur.execute("SELECT url, desired_price, last_price FROM items WHERE user_id=%s", [id])
    items = cur.fetchall()

    return render_template('account.html', user=user, items=items)




def do_login(username='', passwd=''):
    if username == '':
        raise ValueError
    conn = get_database_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT password FROM accounts WHERE username = %s", (username,))
    db_password = cur.fetchone()[0]
    if not pbkdf2_sha256.verify(passwd, db_password):
        raise ValueError
    session['logged_in'] = True
    session['username'] = username


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    error = {'error': ""}
    if request.method == 'POST':

        username = request.form['signup_username']
        email = request.form['signup_email']
        password = request.form['signup_password']
        confirm_password = request.form['signup_password_confirm']

        if password == confirm_password:
            try:
                do_signup(username, email, password)

            except Exception :
                error = {'error': "Username already taken."}
            else:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('home_page'))
        else:
            error = {'error': "Passwords do not match."}

    return render_template('signup.html', error=error)


def do_signup(username='', email='', password=''):
    DB_USER_INSERT = """
INSERT INTO accounts (username, email, password, created)
VALUES (%s, %s, %s, %s)
"""
    conn = get_database_connection()
    cur = conn.cursor()
    now = datetime.datetime.utcnow()
    password = pbkdf2_sha256.encrypt(password)

    cur.execute(DB_USER_INSERT, [username, email, password, now])  #encrypt password

@app.route("/submititems", methods=['GET', 'POST'])
def submititems():
    data = request.get_json()
    conn = get_database_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM accounts WHERE username=%s",
                (session['username'],))
    user_id = cur.fetchone()[0]
    cur.executemany("INSERT INTO items (user_id, url, desired_price, last_price) VALUES (%s, %s, %s, %s)",
                    [(user_id, item['url'], item['desired_price'], item['last_price']) for item in data])
    return url_for('account')


@app.route("/deleteitems", methods=['GET', 'POST'])
def deleteitems():
    data = request.get_json()
    conn = get_database_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM accounts WHERE username=%s",
                (session['username'],))
    user_id = cur.fetchone()[0]
    cur.executemany("DELETE FROM items WHERE user_id=%s AND url=%s",
                    [(user_id, url) for url in data])
    return url_for('account')



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/myaccount")
def account():
    if session['logged_in'] is True:
        conn = get_database_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT username, email FROM accounts WHERE username = %s",
            (session['username'],))
        results = cur.fetchone()
        user = {
            'username': results[0],
            'email': results[1]
        }
        cur.execute("SELECT id FROM accounts WHERE username=%s",
                    (session['username'],))
        user_id = cur.fetchone()
        cur.execute("SELECT url, desired_price, last_price FROM items WHERE user_id=%s", (user_id,))
        items = cur.fetchall()
        return render_template('account.html', user=user, items=items)
    else:
        return redirect(url_for('home_page'))


app.config['DATABASE'] = os.environ.get(
    'DATABASE_URL',
)#dbname=lowr user=lowr_user password=lowr
app.config['ADMIN_USERNAME'] = os.environ.get(
    'ADMIN_USERNAME', 'admin'
)

app.config['ADMIN_PASSWORD'] = os.environ.get(
    'ADMIN_PASSWORD', pbkdf2_sha256.encrypt('admin')
)

app.config['SECRET_KEY'] = os.environ.get(
    'FLASK_SECRET_KEY',
)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        if exception and isinstance(exception, psycopg2.Error):
            db.rollback()
        else:
            db.commit()
        db.close()
        g.db = None  # get rid of db from the g namespace


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),  404


if __name__ == '__main__':
    from gevent.wsgi import WSGIServer
    app.debug = True
    http_server = WSGIServer(('', 8080), app)
    http_server.serve_forever()
