from app.main.forms import NameForm
from flask import flash, render_template
from . import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = NameForm()
    flash('欢迎回来！')
    return render_template('auth/login.html', title='登陆', form=form)
