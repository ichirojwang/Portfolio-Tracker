from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flasktracker.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "warning"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from flasktracker.users.routes import users
    from flasktracker.portfolios.routes import portfolios
    from flasktracker.errors.handlers import errors
    from flasktracker.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(portfolios)
    app.register_blueprint(errors)
    app.register_blueprint(main)

    from flasktracker.portfolios.utils import round_not_whole, format_dollar, format_pl, format_percent
    app.jinja_env.globals.update(round=round_not_whole)
    app.jinja_env.globals.update(format_dollar=format_dollar)
    app.jinja_env.globals.update(format_pl=format_pl)
    app.jinja_env.globals.update(format_percent=format_percent)

    return app
