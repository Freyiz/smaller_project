from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_pagedown import PageDown
from flask_moment import Moment
from flask_mail import Mail

bootstrap = Bootstrap()
db = SQLAlchemy()
page_down = PageDown()
moment = Moment()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '客官请登陆!'
login_manager.session_protection = 'strong'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    page_down.init_app(app)
    moment.init_app(app)
    mail.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
