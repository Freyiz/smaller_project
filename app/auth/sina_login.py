from flask_login import login_user
from flask import session, redirect, url_for, request, flash
from app import oauth, db
from ..models import User
from . import auth
import json
import os

SINA_APP_ID = os.getenv('SINA_APP_ID')
SINA_APP_KEY = os.getenv('SINA_APP_KEY')

sina = oauth.remote_app(
    'sina',
    consumer_key=SINA_APP_ID,
    consumer_secret=SINA_APP_KEY,
    base_url='https://api.weibo.com',
    request_token_url=None,
    access_token_url='/oauth2/access_token',
    authorize_url='/oauth2/authorize',
)


@auth.route('/sina-user-info')
def sina_user_info():
    if 'sina_token' in session:
        return redirect(request.args.get('next') or url_for('main.index'))
    return redirect(url_for('auth.sina_login'))


@auth.route('/sina-login')
def sina_login():
    return sina.authorize(callback=url_for('auth.sina_authorized', _external=True))


@auth.route('/sina-authorized')
def sina_authorized():
    resp = sina.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['sina_token'] = ''

    return redirect(url_for('auth.sina_user_info'))


@sina.tokengetter
def get_sina_oauth_token():
    return session.get('sina_token')
