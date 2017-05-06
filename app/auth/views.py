from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from flask import flash, render_template, redirect, url_for, request, session, make_response
from . import auth
from ..models import User, db
from flask_login import login_user, logout_user, login_required, current_user
from ..email import send_email


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '验证邮箱', 'auth/email/confirm', user=user, token=token)
        flash('注册成功，一封确认邮件已经发往你的邮箱，请注意查收哦！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint != 'main.index' \
                and request.endpoint != 'main.about' \
                and request.endpoint != 'main.user' \
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
    import random

    def rndChar():
        return chr(random.randint(65, 90))

    def rndColor():
        return random.randint(64, 255), random.randint(64, 255), random.randint(64, 255)

    def rndColor2():
        return random.randint(32, 127), random.randint(32, 127), random.randint(32, 127)

    def line():
        return random.randint(1, 240), random.randint(1, 60), random.randint(1, 240), random.randint(1, 60)

    img = Image.new('RGBA', (240, 60), (255, 255, 255))
    font = ImageFont.truetype('fonts/yahei.ttf', 36)
    draw = ImageDraw.Draw(img)
    for x in range(0, img.size[0], 2):
        for y in range(0, img.size[1]):
            draw.point((x, y), fill=rndColor())
    strs = ''
    for i in range(4):
        each_str = rndChar()
        img1 = Image.new('RGBA', (51, 51), (255, 255, 255, 0))
        img_font = ImageDraw.Draw(img1)
        img_font.text((1, 1), each_str, font=font, fill=rndColor2())
        img1 = img1.rotate(random.randint(-30, 30))
        img.paste(img1, (10 + i * 60, 10), mask=img1)
        strs += each_str
    draw.line(line(), rndColor2())
    draw.line(line(), rndColor2())
    draw.line(line(), rndColor2())
    draw.line(line(), rndColor2())
    img = img.filter(ImageFilter.SMOOTH_MORE)
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
    form = LoginForm()
    if form.validate_on_submit():
        if 'code_text' in session and form.verification_code.data.lower() \
                != session['code_text'].lower():
            flash('验证码不正确！')
            return render_template('auth/login.html', form=form)
        user = User.query.filter_by(email=form.username_or_email.data).first() or \
                 User.query.filter_by(username=form.username_or_email.data).first()
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
    session.pop('code_text')
    logout_user()
    flash('See you again!')
    return redirect(url_for('main.index'))


@auth.route('/delete')
@login_required
def delete():
    db.session.delete(current_user)
    db.session.commit()
    return redirect(url_for('main.index'))
