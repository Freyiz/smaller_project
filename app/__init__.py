from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from flask_sqlalchemy import SQLAlchemy
from .config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
nav = Nav()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config['default'])

    nav.register_element('top', Navbar('Welcome',
                                       View('主页', 'index'),
                                       View('登陆', 'login'),
                                       View('上传', 'upload'),
                                       View('进攻', 'attack'),
                                       View('关于', 'about'),
                                       ))
    nav.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    #config['default'].init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
