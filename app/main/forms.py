from wtforms import StringField, SubmitField, TextAreaField, \
    BooleanField, SelectField, ValidationError, FileField
from wtforms.validators import DataRequired, Length, Regexp, Email
from flask_wtf import FlaskForm, RecaptchaField
from flask_pagedown.fields import PageDownField
from ..models import Role, User
from flask import current_app


class PostForm(FlaskForm):
    body = PageDownField('公告牌', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    body = PageDownField('评论', validators=[DataRequired()])
    submit = SubmitField('发表')


class EditProfileForm(FlaskForm):
    avatar = FileField('更改头像')
    name = StringField('头衔')
    location = StringField('地址')
    about_me = TextAreaField('简介')
    submit = SubmitField('提交')

    def validate_avatar(self, field):
        if '.' not in field.data.filename or field.data.filename.rsplit('.')[1] \
                not in current_app.config['ALLOWED_EXTENSIONS']:
            raise ValidationError('确保文件后缀为其中之一：%s' % current_app.config['ALLOWED_EXTENSIONS'])


class EditProfileAdminForm(FlaskForm):
    confirmed = BooleanField('邮箱验证')
    role = SelectField('角色权限', coerce=int)
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('角色名', validators=[DataRequired(),
                Regexp(r'^[\u4E00-\u9FA5]{2,6}$|^[A-Za-z]{2,12}$', 0, '角色名为2~12位字母或2~6位汉字。')])
    name = StringField('头衔')
    location = StringField('地址')
    about_me = TextAreaField('简介')
    submit = SubmitField('确定')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册。')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('角色名已存在。')


class RecaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField('确定')


class DemotionForm(FlaskForm):
    submit = SubmitField('忏悔')


class JumpForm(FlaskForm):
    page_num = StringField(validators=[DataRequired()])
    submit = SubmitField('传送')


class SearchForm(FlaskForm):
    keywords = StringField(validators=[DataRequired()])
    submit = SubmitField('查找')
