from flask_login import login_user
from flask import session, redirect, url_for, request, flash
from app import oauth, db
from ..models import User
from . import auth
import json
import os

QQ_APP_ID = os.getenv('QQ_APP_ID')
QQ_APP_KEY = os.getenv('QQ_APP_KEY')

qq = oauth.remote_app(
    'qq',
    consumer_key=QQ_APP_ID,
    consumer_secret=QQ_APP_KEY,
    base_url='https://graph.qq.com',
    request_token_url=None,
    request_token_params={'scope': 'get_user_info'},
    access_token_url='/oauth2.0/token',
    authorize_url='/oauth2.0/authorize',
)


def json_to_dict(data):
    data = bytes.decode(data)
    if data.find('callback') > -1:
        pos_lb = data.find('{')
        pos_rb = data.find('}')
        data = data[pos_lb:pos_rb + 1]
    try:
        return json.loads(data, encoding='utf-8')
    except:
        return data


def update_qq_api_request_data(data={}):
    defaults = {
        'openid': session.get('qq_openid'),
        'access_token': session.get('qq_token')[0],
        'oauth_consumer_key': QQ_APP_ID,
    }
    defaults.update(data)
    return defaults


@auth.route('/qq-user-info')
def qq_user_info():
    if 'qq_token' in session:
        data = update_qq_api_request_data()
        resp = qq.get('/user/get_user_info', data=data)
        data = json_to_dict(resp.data)
        user = User.query.filter_by(username=data.get('nickname')).first()
        if not user:
            user = User(username=data.get('nickname'), avatar=data.get('figureurl_qq_2'), confirmed=True)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash('欢迎回来！%s' % user.username)
        return redirect(request.args.get('next') or url_for('main.index'))
    return redirect(url_for('auth.qq_login'))


@auth.route('/qq-login')
def qq_login():
    return qq.authorize(callback=url_for('auth.qq_authorized', _external=True))


@auth.route('/qq-authorized')
def qq_authorized():
    resp = qq.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['qq_token'] = (resp['access_token'], '')

    resp = qq.get('/oauth2.0/me', {'access_token': session['qq_token'][0]})
    resp = json_to_dict(resp.data)
    if isinstance(resp, dict):
        session['qq_openid'] = resp.get('openid')

    return redirect(url_for('auth.qq_user_info'))


@qq.tokengetter
def get_qq_oauth_token():
    return session.get('qq_token')
