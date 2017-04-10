from app.main.forms import LoginForm, RegistrationForm
from flask import flash, render_template, redirect, url_for, request
from . import auth
from ..models import User, db
from flask_login import login_user, logout_user, login_required
from config import Config
import os


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
        flash('注册成功啦！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data, password=form.password.data).first()
        if user:
            login_user(user)
            flash('欢迎回来！')
            return redirect(url_for('main.index'))
        flash('用户名或密码不正确哦！')
    return render_template('auth/login.html', title='登陆', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出！')
    return redirect(url_for('auth.login'))


@auth.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    text = ''
    if request.method == 'POST':
        f = request.files['file']
        if f:
            filename = f.filename
            if f.filename in os.listdir(Config.UPLOAD_FOLDER):
                text = '文件已存在！'
            else:
                text = '上传成功！'
            # secure_filename（） 不识别汉字的问题尚未解决
            # filename = secure_filename(f.filename)
            # if filename == 'py':
            # filename = '12345.py'
            f.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            # return redirect(url_for('upload'), filename=filename)
        else:
            text = '未找到文件！'
    return render_template('auth/upload.html', text=text)


@auth.route('/attack')
@login_required
def attack():
    return render_template('attack.html')
