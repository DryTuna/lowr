from flask import Flask
from flask import render_template
from amazon_book_scraper import *


app = Flask(__name__)


@app.route('/')
def main():
    return render_template()


if __name__ == '__main__':
    app.run(debug=True)
