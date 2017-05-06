import os
import json
from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_oauthlib.client import OAuth

if os.path.exists('.env'):
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2 and var[0].startswith('REN2'):
            os.environ[var[0]] = var[1]

ren2_id = os.environ.get('REN2_APP_ID')
ren2_key = os.environ.get('REN2_APP_KEY')

ren2 = oauth.remote_app(
    'ren2',
    consumer_key=ren2_id,
    consumer_secret=ren2_key,
    base_url='https://graph.renren.com',
    request_token_url=None,
    access_token_url='/oauth/token',
    authorize_url='/oauth/authorize'
)


@main.route('/user-info')
def get_user_info():
    if 'ren2_token' in session:
        return redirect(session['user']['avatar'][0]['url'])
    return redirect(url_for('.ren2_login'))


@main.route('/ren2-login')
def ren2_login():
    return ren2.authorize(callback=url_for('.ren2_authorized', _external=True))


@main.route('/ren2-authorized')
def ren2_authorized():
    resp = ren2.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['ren2_token'] = (resp['access_token'], '')

    # Get openid via access_token, openid and access_token are needed for API calls
    if isinstance(resp, dict):
        session['user'] = resp.get('user')
    return redirect(url_for('.get_user_info'))


@ren2.tokengetter
def get_ren2_token():
    return session.get('ren2_token')
