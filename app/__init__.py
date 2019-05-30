import os
import time
import datetime
from datetime import datetime

from flask import Flask, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from flask_login import LoginManager


#SETTING UP FLASK_APP
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

#WAIT TO SEE IF NEEDED
app.config["SECRET_KEY"] = '8b204a070795bf8203b56a5258d7bcc6'

'''
If i dont want to use cookies; use the text below and then also include {{ form.csrf_token }} in templates.

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
'''

##THIS IS WHERE THE DB GOES
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

from app import routes