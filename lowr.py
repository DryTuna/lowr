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

from amazon_book_scraper import extract_books, fetch_search_results, parse_source



app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template('main.html')
<<<<<<< HEAD
=======


@app.route("/books")
def book_serve():
    keyworkds = data.keyword
    rn = 'n:283155'
    min_p = data.price
    page = 1
    price_range = data.range

    file_ = []
    content, content_encoding = fetch_search_results(keyworkds, rn, page, min_p, price_range)
    parsed_content = parse_source(content[0], content_encoding).find_all('div', class_='result')
    extracted_content = extracted_content(parsed_content, min_p, price_range)

        for every_item in extracted_content:
            file.write(str(every_item) + "\n")




    return render_template('main.html')

>>>>>>> master

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)