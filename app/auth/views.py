from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from flask import flash, render_template, redirect, url_for, request
from . import auth
from ..models import User, db
from flask_login import login_user, logout_user, login_required, current_user
from ..email import send_email


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.name.data,
                    password=form.password.data
                    )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '验证邮箱', 'auth/email/confirm', user=user, token=token)
        flash('注册成功啦，一封确认邮件已经发往你的邮箱，请注意查收哦！')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint != 'main.index' \
            and request.endpoint != 'main.about' \
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
    return render_template('index.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.name_or_email.data).first() or \
                 User.query.filter_by(username=form.name_or_email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('欢迎回来！%s' % user.username)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码不正确！')
    return render_template('auth/login.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('密码修改成功!')
            return redirect(url_for('main.index'))
        flash('密码错误！')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            token = current_user.generate_confirmation_token()
            send_email(current_user.email, '重置密码', 'auth/email/reset_password',
                       user=current_user, token=token)
            flash('一封确认邮件已经发往你的邮箱，请注意查收哦！')
            return redirect(url_for('main.index'))
        flash('邮箱错误！')
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.confirm(token):
        flash('链接失效！')
        return redirect(url_for('main.index'))
    else:
        form = PasswordResetForm()
        if form.validate_on_submit():
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('密码重置成功!')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.new_email = form.email.data
            db.session.add(current_user)
            db.session.commit()
            token = current_user.generate_confirmation_token()
            send_email(current_user.email, '验证新邮箱', 'auth/email/change_email',
                       user=current_user, token=token)
            flash('一封确认邮件已经发往你的新邮箱，请注意查收哦！')
            return redirect(url_for('main.index'))
        flash('密码错误！')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
def change_email(token):
    if not current_user.confirm(token):
        flash('链接失效！')
        return redirect(url_for('main.index'))
    else:
        current_user.email = current_user.new_email
        db.session.add(current_user)
        db.session.commit()
        flash('邮箱修改成功!')
    return render_template('index.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('See you again!')
    return redirect(url_for('main.index'))


@auth.route('/delete')
@login_required
def delete():
    db.session.delete(current_user)
    db.session.commit()
    return render_template('index.html')