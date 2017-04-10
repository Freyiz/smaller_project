import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    UPLOAD_FOLDER = r'D:\my_project\app\static\uploads'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'hard to change'

config = {
    'default': Config
}