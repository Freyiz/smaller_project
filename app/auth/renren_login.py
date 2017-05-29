from flask_login import login_user
from flask import session, redirect, url_for, request, flash
from app import oauth, db
from ..models import User
from . import auth
import json
import os

REN2_APP_ID = os.environ.get('REN2_APP_ID')
REN2_APP_KEY = os.environ.get('REN2_APP_KEY')

ren2 = oauth.remote_app(
    'ren2',
    consumer_key=REN2_APP_ID,
    consumer_secret=REN2_APP_KEY,
    base_url='https://graph.renren.com',
    request_token_url=None,
    access_token_url='/oauth/token',
    authorize_url='/oauth/authorize'
)


@auth.route('/ren2-user-info')
def ren2_user_info():
    if 'ren2_user' in session:
        user = User.query.filter_by(username=session['ren2_user']['name']).first()
        if not user:
            user = User(username=session['ren2_user']['name'], avatar=session['ren2_user']['avatar'][3]['url'], confirmed=True)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash('欢迎回来！%s' % user.username)
        return redirect(request.args.get('next') or url_for('main.index'))
    return redirect(url_for('auth.ren2_login'))


@auth.route('/ren2-login')
def ren2_login():
    return ren2.authorize(callback=url_for('.ren2_authorized', _external=True))


@auth.route('/ren2-authorized')
def ren2_authorized():
    resp = ren2.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, dict):
        session['ren2_user'] = resp.get('user')
    return redirect(url_for('.ren2_user_info'))


@ren2.tokengetter
def get_ren2_token():
    return session.get('ren2_token')
