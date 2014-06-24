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

from amazon_book_scraper import extract_books, fetch_search_results, parse_source, search_result



app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template('main.html')


@app.route("/books")
def book_serve():
    keyworkds = data.keyword
    category = 'n:283155'
    price = data.price
    price_range = data.range

    file_ = []
    content_queue = search_result(keyworkds, category, price, price_range)
    while True:
        try:
            file.append(content_queue.pop()._data)
        except IndexError:
            break

    return render_template('search.html', file_)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)