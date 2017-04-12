import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'hard to change?'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = r'D:\my_project\app\static\uploads'
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <562124140@qq.com>'

#    @staticmethod
#    def init_app(app):
#        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {'development': DevelopmentConfig,
          'testing': TestingConfig,
          'production': ProductionConfig,
          'default': DevelopmentConfig}