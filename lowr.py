from flask import Flask
from flask import render_template
from amazon_book_scraper import *


cat = {
    'Electronics': 'n:283155',
    'Books': 'n:283155'
}


app = Flask(__name__)


@app.route('/')
def main():
    return render_template("main.html")


if __name__ == '__main__':
    app.run(debug=True)
