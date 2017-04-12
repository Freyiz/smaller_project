from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, Regexp
from flask_wtf import FlaskForm
from app.models import User


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    name = StringField('用户名', validators=[DataRequired(), Length(2, 20),
                Regexp(r'^[a-zA-z][\w]*$', 0, '用户名必须以字母开头，只能包含数字、字母或下划线。')])
    password = PasswordField('密码 ', validators=[DataRequired(),
                Length(6, 20, message='密码长度至少6位！'),
                EqualTo('password2', message='两次输入密码不一致！'),
                Regexp(r'^[a-zA-z0-9]*([a-zA-Z][0-9]|[0-9][a-zA-Z])[a-zA-Z0-9]*$',
                       0, '密码必须由数字和字母组成！')])
    password2 = PasswordField('确认密码 ', validators=[DataRequired()])
    submit = SubmitField('注册')

    @staticmethod
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('哎哟，被别人注册过了~')

    @staticmethod
    def validate_name(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('名字被征用啦，换一个吧~')


class LoginForm(FlaskForm):
    name_or_email = StringField('用户名/邮箱', validators=[DataRequired()])
    password = PasswordField('密码 ', validators=[DataRequired()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('提交')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码 ', validators=[DataRequired(),
                Length(6, 20, message='密码长度至少6位！'),
                EqualTo('password2', message='两次输入密码不一致！'),
                Regexp(r'^[a-zA-z0-9]*([a-zA-Z][0-9]|[0-9][a-zA-Z])[a-zA-Z0-9]*$',
                       0, '密码必须由数字和字母组成！')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired()])
    submit = SubmitField('提交')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码 ', validators=[DataRequired(),
                Length(6, 20, message='密码长度至少6位！'),
                EqualTo('password2', message='两次输入密码不一致！'),
                Regexp(r'^[a-zA-z0-9]*([a-zA-Z][0-9]|[0-9][a-zA-Z])[a-zA-Z0-9]*$',
                       0, '密码必须由数字和字母组成！')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交')


class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('提交')

    @staticmethod
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('哎哟，被别人注册过了~')