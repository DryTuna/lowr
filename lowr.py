# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
from flask import request

from amazon_scraper import search_results as uni_search
from amazon_book_scraper import search_results as book_search

app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template('main.html')


@app.route("/search", methods=['GET', 'POST'])
def search():
    import json

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

    print category
    if category == 'Books' or \
       category == 'CDs & Vinyl' or \
       category == 'Software' or \
       category == 'Video Games':
        file_ = book_search(keywords, category, price, price_range)
    else:
        file_ = uni_search(keywords, category, price, price_range)

    results = []

    while True:
        try:
            results.append(file_.pop()._data)
        except IndexError:
            break
    return render_template('search.html', results=results)


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/logout")
def logout():
    pass


@app.route("/signup")
def signup():
    return render_template('signup.html')


@app.route("/submititems", methods=['GET', 'POST'])
def submititems():
    import json
    data = request.get_json()
    print data
    return '/myaccount'


@app.route("/myaccount")
def account():
    user = {'username': "joe_public",
            'email': 'average@joe.com'}  # TESTING ONLY
    item_urls = [u'http://www.amazon.com/Marshall-Amplification-MF4400-NA-Fridge/dp/B008K4FTV8',
                 u'http://www.amazon.com/Avanti-Model-RMS550PS-SIDE-BY-SIDE-Refrigerator/dp/B00GHIJNY8',
                 u'http://www.amazon.com/Energy-Star-Refrigerator-Top-Mount-Freezer/dp/B00CSBL3AU',
                 u'http://www.amazon.com/Mid-Size-Frost-Free-Refrigerator-Top-Mount-Freezer/dp/B00DAI2TCQ']
    return render_template('account.html', user=user, item_urls=item_urls)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
