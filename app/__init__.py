from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_pagedown import PageDown
from flask_moment import Moment
from flask_mail import Mail
from flask_oauthlib.client import OAuth
# from flask_babel import Babel, gettext as _

bootstrap = Bootstrap()
db = SQLAlchemy()
page_down = PageDown()
moment = Moment()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '军情七处特派员沃尔森·弗利摩尔需要查看你的通行证!'
login_manager.session_protection = 'strong'
# babel = Babel()
oauth = OAuth()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    page_down.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    # babel.init_app(app)
    oauth.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1.0')

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    return app
