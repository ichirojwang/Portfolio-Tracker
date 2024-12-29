import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flasktracker.helper import round_not_whole, format_dollar, format_pl, format_percent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('PG_FLASK_TRACKER')
app.jinja_env.globals.update(round=round_not_whole)
app.jinja_env.globals.update(format_dollar=format_dollar)
app.jinja_env.globals.update(format_pl=format_pl)
app.jinja_env.globals.update(format_percent=format_percent)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

from flasktracker import routes
