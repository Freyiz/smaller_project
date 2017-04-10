from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length, Email, Regexp
from flask_wtf import FlaskForm
from app.models import User


class LoginForm(FlaskForm):
    name = StringField('用户名/邮箱', validators=[DataRequired()])
    password = PasswordField('密码 ', validators=[DataRequired()])
    submit = SubmitField('提交')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    name = StringField('用户名', validators=[DataRequired(), Length(1, 20),
                                          Regexp(r'^[a-zA-z][\w]*$', 0, '用户名必须以字母开头且只能包含数字、字母或下划线')
                                          ])
    password = PasswordField('密码 ', validators=[DataRequired(),
                                                EqualTo('password2', message='密码不一致！')])
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
