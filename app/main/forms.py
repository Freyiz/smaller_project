from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField


class PostForm(FlaskForm):
    body = PageDownField('写下你的想法', validators=[DataRequired()])
    submit = SubmitField('发表')


class CommentForm(FlaskForm):
    body = PageDownField('评论', validators=[DataRequired()])
    submit = SubmitField('发表')
