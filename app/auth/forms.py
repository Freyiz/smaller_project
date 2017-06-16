from wtforms import StringField, PasswordField, SubmitField, \
    ValidationError, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, Regexp
from flask_wtf import FlaskForm
from app.models import User


class RegistrationForm(FlaskForm):
    wow_faction = StringField('阵营')
    wow_race = StringField('种族')
    wow_class = StringField('职业')
    username = StringField('角色名', validators=[DataRequired(),
                Regexp(r'^[\u4E00-\u9FA5]{2,6}$|^[A-Za-z]{2,12}$', 0, '角色名为2~12位字母或2~6位汉字。')])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email(message='邮箱名称无效。')])
    password = PasswordField('密码', validators=[DataRequired(),
                Length(6, 64, message='密码长度至少6位。'),
                EqualTo('password2', message='两次输入密码不一致。'),
                Regexp(r'^[a-zA-z0-9]*([a-zA-Z][0-9]|[0-9][a-zA-Z])[a-zA-Z0-9]*$',
                       0, '密码必须由数字和字母组成。')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    verification_code = StringField('验证码', validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.title()).first():
            raise ValidationError('角色名已存在。')


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('自动登录')
    submit = SubmitField('进入艾泽拉斯')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[DataRequired(),
                Length(6, 64, message='密码长度至少6位。'),
                EqualTo('password2', message='两次输入密码不一致。'),
                Regexp(r'^[a-zA-z0-9]*([a-zA-Z][0-9]|[0-9][a-zA-Z])[a-zA-Z0-9]*$',
                       0, '密码必须由数字和字母组成。')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱不正确。')


class PasswordResetForm(FlaskForm):
    email = StringField('邮箱')
    password = PasswordField('新密码', validators=[DataRequired(),
                Length(6, 64, message='密码长度至少6位。'),
                EqualTo('password2', message='两次输入密码不一致。'),
                Regexp(r'^[a-zA-z0-9]*([a-zA-Z][0-9]|[0-9][a-zA-Z])[a-zA-Z0-9]*$',
                       0, '密码必须由数字和字母组成。')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱不正确。')


class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册。')
