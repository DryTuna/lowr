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



app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)