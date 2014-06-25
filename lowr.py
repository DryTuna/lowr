# -*- coding: utf-8 -*-

from flask import Flask
import os
from contextlib import closing
from flask import g
import datetime
from flask import render_template
from flask import abort
from flask import request
from flask import url_for
from flask import redirect
from flask import session

from amazon_book_scraper import search_result



app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template('main.html')


@app.route("/search", methods=['GET', 'POST'])
def search():
    import json

    amazon_categories = {'All Departments': 'i:aps',
                        'Amazon Instant Video': 'n:2858778011',
                        'Appliances': 'n:2619525011',
                        'Apps for Android' : 'n:2350149011',
                        'Arts, Crafts & Sewing': 'n:2617941011',
                        'Automotive': 'n:15684181',
                        'Baby': 'n:165796011',
                        'Beauty': 'n:3760911',
                        'Books' : 'n:283155',
                        'Cell Phones & Accessories' : 'n:2335752011',
                        'Clothing & Accessories': 'n:1036592',
                        'Collectibles & Fine Art': 'n:4991425011',
                        'Computers' : 'n:541966',
                        'CDs & Vinyl' : 'n:5174',
                        'Digital Music' : 'n:163856011',
                        'Electronics': 'n:172282',
                        'Gift Cards Store' : 'n:2238192011',
                        'Grocery & Gourmet Food': 'n:16310101',
                        'Health & Personal Care': 'n:3760901',
                        'Home & Kitchen': 'n:1055398',
                        'Industrial & Scientific': 'n:16310091',
                        'Jewelry': 'n:3367581',
                        'Kindle Store': 'n:133140011',
                        'Magazine Subscriptions': 'n:599858',
                        'Movies & TV': 'n:2625373011',
                        'Musical Instruments': 'n:11091801',
                        'Office Products': 'n:1064954',
                        'Patio, Lawn & Garden': 'n:2972638011',
                        'Pet Supplies' : 'n:2619533011',
                        'Shoes': 'n:672123011',
                        'Software': 'n:229534',
                        'Sports & Outdoors': 'n:3375251',
                        'Tools & Home Improvement': 'n:228013',
                        'Toys & Games': 'n:165793011',
                        'Video Games': 'n:468642',
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

    file_ = search_result(keywords, 'n:283155', price, price_range)

    results = []

    while True:
        try:
            results.append(file_.pop()._data)
        except IndexError:
            break

    print file_

    print results

    return render_template('search.html', results = results)#{'title':'game of thornes', 'imgage':'adfhasjd', 'price':200    })


@app.route("/login")
def login():
    pass


@app.route("/logout")
def logout():
    pass

@app.route("/signup")
def signup():
    pass


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)