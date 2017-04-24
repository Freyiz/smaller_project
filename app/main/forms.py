# coding=utf-8
from wtforms import StringField, SubmitField, TextAreaField, \
    BooleanField, SelectField, ValidationError, FileField
from wtforms.validators import DataRequired, Length, Regexp, Email
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from ..models import Role, User
from flask import current_app


class PostForm(FlaskForm):
    body = PageDownField('随便写写', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    body = PageDownField('评论', validators=[DataRequired()])
    submit = SubmitField('发表')


class EditProfileForm(FlaskForm):
    avatar = FileField('更改头像')
    name = StringField('姓名')
    location = StringField('地址')
    about_me = TextAreaField('简介')
    submit = SubmitField('提交')

    def validate_avatar(self, field):
        if field.data.filename.rsplit('.')[1] not in current_app.config['ALLOWED_EXTENSIONS']:
            raise ValidationError('确保文件后缀为其中之一：%s' % current_app.config['ALLOWED_EXTENSIONS'])


class EditProfileAdminForm(FlaskForm):
    confirmed = BooleanField('邮箱验证')
    role = SelectField('角色权限', coerce=int)
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(2, 20),
                Regexp(r'^[a-zA-z][\w]*$', 0, '用户名必须以字母开头，只能包含数字、字母或下划线。')])
    name = StringField('姓名')
    location = StringField('地址')
    about_me = TextAreaField('简介')
    submit = SubmitField('确定')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in  Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('哎哟，被别人注册过了~')

    def validate_name(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('名字被征用啦，换一个吧~')
