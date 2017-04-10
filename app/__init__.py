from flask import Flask
from flask_bootstrap import Bootstrap
# from flask_nav import Nav
# from flask_nav.elements import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
# nav = Nav()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '大王请登陆先!'
login_manager.session_protection = 'strong'


def create_app():
    app = Flask(__name__)
    app.config.from_object(config['default'])
    # nav.register_element('top', Navbar('Welcome',
                                       # View('主页', 'main.index'),
                                       # View('登陆', 'auth.login'),
                                       # View('上传', 'main.upload'),
                                       # View('进攻', 'main.attack'),
                                       # View('关于', 'main.about'),
                                       # View('注册', 'auth.register'),
                                       # View('退出', 'auth.logout'),
                                       # ))
    # nav.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    # config['default'].init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
