from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from flask import flash, render_template, redirect, url_for, request, \
    session, make_response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, db, WowConfig
from .._email import send_email
from app import oauth
from . import auth
import json
import os


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if 'code_text' in session and form.verification_code.data.lower() \
                != session['code_text'].lower():
            flash('验证码不正确！')
            return render_template('auth/register.html', form=form)
        user = User(wow_faction=form.wow_faction.data,
                    wow_race=form.wow_race.data,
                    wow_class=form.wow_class.data,
                    email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '验证邮箱', 'auth/email/confirm', user=user, token=token)
        flash('注册成功，一封确认邮件已经发往你的邮箱，请注意查收！')
        return redirect(url_for('auth.login'))
    player = WowConfig().random_player()
    form.wow_faction.data = player[0]
    form.wow_race.data = player[1]
    form.wow_class.data = player[2]
    return render_template('auth/register.html', form=form)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint != 'main.index' \
                and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    email_address = 'http://mail.%s' % current_user.email.rsplit('@')[-1]
    return render_template('auth/unconfirmed.html', email_address=email_address)


@auth.route('/confirm')
@login_required
def resend_confirmation():
    if not current_user.confirmed:
        token = current_user.generate_confirmation_token()
        send_email(current_user.email, '验证邮箱', 'auth/email/confirm',
                   user=current_user, token=token)
        flash('一封确认邮件已经发往你的邮箱，请注意查收哦！')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('验证成功！')
    else:
        flash('链接失效！')
    return redirect(url_for('main.index'))


def generate_verification_code():
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    from random import randint, choice

    def char():
        return chr(choice((randint(48, 57), randint(65, 90), randint(97, 122))))

    def line():
        return randint(1, 220), randint(1, 40), randint(1, 220), randint(1, 40)

    def alliance_or_horde():
        return choice(((127, 0, 0), (0, 120, 255)))

    img = Image.new('RGBA', (220, 40), (231,231,231))
    font = ImageFont.truetype('app/static/fonts/yahei.ttf', 30)
    draw = ImageDraw.Draw(img)

    strs = ''
    for i in range(4):
        each_str = char()
        img1 = Image.new('RGBA', (50, 40), (0, 0, 0, 0))
        img_font = ImageDraw.Draw(img1)
        img_font.text((1, 1), each_str, font=font, fill=alliance_or_horde())
        img1 = img1.rotate(randint(-30, 30))
        img.paste(img1, (10 + i * 50, 0), mask=img1)
        strs += each_str
    draw.line(line(), alliance_or_horde())
    draw.line(line(), alliance_or_horde())
    draw.line(line(), alliance_or_horde())
    img = img.filter(ImageFilter.SMOOTH)
    return img, strs


@auth.route('/verification-code/')
def verification_code():
    from io import BytesIO

    output = BytesIO()
    code_img, code_str = generate_verification_code()
    code_img.save(output, 'jpeg')
    img_data = output.getvalue()
    output.close()
    response = make_response(img_data)
    response.headers['Content-Type'] = 'image/jpg'
    session['code_text'] = code_str
    return response


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('欢迎回来！%s' % user.username)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名/邮箱或密码不正确！')
    return render_template('auth/login.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('密码修改成功!')
            return redirect(url_for('main.index'))
        flash('密码不正确！')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_confirmation_token()
        send_email(user.email, '重置密码', 'auth/email/reset_password',
                   user=user, token=token)
        flash('一封确认邮件已经发往你的邮箱，请注意查收哦！')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.confirm(token):
            user.password = form.password.data
            db.session.add(user)
            flash('密码重置成功!')
            return redirect(url_for('auth.login'))
        flash('邮箱不正确或链接失效！！')
        return redirect(url_for('auth.password_reset', token=token))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '验证新邮箱', 'auth/email/change_email',
                       user=current_user, token=token)
            flash('一封确认邮件已经发往你的新邮箱，请注意查收哦！')
            return redirect(url_for('main.index'))
        flash('密码不正确！')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
def change_email(token):
    if not current_user.change_email(token):
        flash('链接失效！')
    else:
        flash('邮箱修改成功!')
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    session.pop('code_text', None)
    session.pop('qq_token', None)
    session.pop('qq_openid', None)
    session.pop('ren2_token', None)
    session.pop('ren2_user', None)
    session.pop('sina_token', None)
    session.pop('accord', None)
    logout_user()
    flash('See you again!')
    return redirect(url_for('main.index'))


@auth.route('/clause')
def clause():
    return render_template('auth/clause.html')


@auth.route('/player')
def player():
    player = WowConfig().random_player()
    return jsonify(wow_faction=player[0], wow_race=player[1], wow_class=player[2])


@auth.route('/delete')
@login_required
def delete():
    db.session.delete(current_user)
    db.session.commit()
    return redirect(url_for('main.index'))


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
            user = User(username=data.get('nickname'),
                        avatar=data.get('figureurl_qq_2'), confirmed=True)
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
        print(session['ren2_user'])
        user = User.query.filter_by(username=session['ren2_user']['name']).first()
        if not user:
            user = User(username=session['ren2_user']['name'],
                        avatar=session['ren2_user']['avatar'][3]['url'], confirmed=True)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash('欢迎回来！%s' % user.username)
        return redirect(request.args.get('next') or url_for('main.index'))
    return redirect(url_for('auth.ren2_login'))


@auth.route('/ren2-login')
def ren2_login():
    return ren2.authorize(callback=url_for('auth.ren2_authorized', _external=True))


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
    return redirect(url_for('auth.ren2_user_info'))


@ren2.tokengetter
def get_ren2_token():
    return session.get('ren2_token')

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
