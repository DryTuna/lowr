# -*- coding: utf-8 -*-


#  GENERAL PURPOSE
import os
import datetime

# FLASK RELATED
from flask import Flask
from flask import g
from flask import redirect
from flask import url_for
from flask import g
from flask import session
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import abort

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
    amazon_categories = {'All Departments': 'i:aps',
                         # 'Amazon Instant Video': 'n:2858778011',
                         'Appliances': 'n:2619525011',
                         # 'Apps for Android' : 'n:2350149011',
                         'Arts, Crafts & Sewing': 'n:2617941011',
                         'Automotive': 'n:15684181',
                         'Baby': 'n:165796011',
                         'Beauty': 'n:3760911',
                         'Books': 'n:283155',
                         'Cell Phones & Accessories': 'n:2335752011',
                         'Clothing & Accessories': 'n:1036592',
                         'Collectibles & Fine Art': 'n:4991425011',
                         'Computers': 'n:541966',
                         'CDs & Vinyl': 'n:5174',
                         # 'Digital Music' : 'n:163856011',
                         'Electronics': 'n:172282',
                         # 'Gift Cards Store' : 'n:2238192011',
                         'Grocery & Gourmet Food': 'n:16310101',
                         'Health & Personal Care': 'n:3760901',
                         'Home & Kitchen': 'n:1055398',
                         'Industrial & Scientific': 'n:16310091',
                         'Jewelry': 'n:3367581',
                         'Kindle Store': 'n:133140011',
                         # 'Magazine Subscriptions': 'n:599858',
                         'Movies & TV': 'n:2625373011',
                         'Musical Instruments': 'n:11091801',
                         'Office Products': 'n:1064954',
                         'Patio, Lawn & Garden': 'n:2972638011',
                         'Pet Supplies': 'n:2619533011',
                         'Shoes': 'n:672123011',
                         # 'Software': 'n:229534',
                         'Sports & Outdoors': 'n:3375251',
                         'Tools & Home Improvement': 'n:228013',
                         'Toys & Games': 'n:165793011',
                         # 'Video Games': 'n:468642',
                         'Watches': 'n:377110011',
                         'Wine': 'n:2983386011'}


    data = json.loads(request.form['data'])
    querey_data = {}
    for item in data:
        if item['name'] == 'search_category':
            querey_data['category'] = amazon_categories[item['value']]
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

    if category == amazon_categories['Books'] or \
       category == amazon_categories['CDs & Vinyl']:
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
        else:
            return redirect(url_for('home_page'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home_page'))



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
            error = {error: "Passwords do not match."}

    return render_template('signup.html', error=error)


def do_signup(username='', email='', password=''):
    DB_USER_INSERT = """
INSERT INTO accounts (username, email, password, created) VALUES (%s, %s, %s, %s)
"""
    conn = get_database_connection()
    cur = conn.cursor()
    now = datetime.datetime.utcnow()
    password = pbkdf2_sha256.encrypt(password)
    cur.execute(DB_USER_INSERT, [username, email, password, now])


@app.route("/submititems", methods=['GET', 'POST'])
def submititems():
    data = request.get_json()
    conn = get_database_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM accounts WHERE username=%s",
                (session['username'],))
    user_id = cur.fetchone()[0]
    print [(user_id, url) for url in data]
    cur.executemany("INSERT INTO urls (user_id, url) VALUES (%s, %s)",
                    [(user_id, url) for url in data])
    return '/myaccount'


@app.route("/myaccount")
def account(user):
    if session['logged_in'] == True:
        return render_template('account.html', user=user)
    else:
        return redirect(url_for('home_page'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

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
        cur.execute("SELECT url FROM urls WHERE user_id=%s", (user_id,))
        item_urls = []
        while True:
            try:
                url = cur.fetchone()[0]
            except (AttributeError, TypeError):
                break
            item_urls.append(url)
        return render_template('account.html', user=user, item_urls=item_urls)
    else:
        return redirect(url_for('home_page'))



app.config['DATABASE'] = os.environ.get(
    'DATABASE_URL', 'dbname=lowr'
)
app.config['ADMIN_USERNAME'] = os.environ.get(
    'ADMIN_USERNAME', 'admin'
)

app.config['ADMIN_PASSWORD'] = os.environ.get(
    'ADMIN_PASSWORD', pbkdf2_sha256.encrypt('admin')
)

app.config['SECRET_KEY'] = os.environ.get(
    'FLASK_SECRET_KEY', 'sooperseekritvaluenooneshouldknow'
)



DB_SCHEMA = """
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    id serial PRIMARY KEY,
    username VARCHAR (127) NOT NULL UNIQUE,
    email VARCHAR (127) NOT NULL,
    password VARCHAR (127) NOT NULL,
    created TIMESTAMP NOT NULL
)
"""



DB_ENTRIES_LIST = """
SELECT id, username , email, password FROM accounts ORDER BY created DESC
"""

DB_ENTRY_LIST = """
SELECT id, username, email, password created FROM accounts WHERE accounts.id = %s
"""

DB_DELETE_ENTRY_LIST = """
DELETE FROM accounts WHERE accounts.id = %s
"""

def connect_db():
    """Return a connection to the configured database"""
    return psycopg2.connect(app.config['DATABASE'])

def init_db():
    """Initialize the database using DB_SCHEMA

    WARNING: executing this function will drop existing tables.
    """
    with closing(connect_db()) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()


def get_database_connection():
    db = getattr(g, 'db', None)
    if db is None:
        g.db = db = connect_db()
    return db


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        if exception and isinstance(exception, psycopg2.Error):
            db.rollback()
        else:
            db.commit()
        db.close()
        g.db = None # get rid of db from the g namespace


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),  404


if __name__ == '__main__':
    from gevent.wsgi import WSGIServer
    app.debug = True
    http_server = WSGIServer(('', 8080), app)
    http_server.serve_forever()

