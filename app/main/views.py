from flask import render_template, send_from_directory, request, redirect, url_for
from . import main
from flask_login import login_required, current_user
from config import Config
import os
from .forms import PostForm, CommentForm
from ..models import Post, Comment
from .. import db
from datetime import datetime


@main.route('/')
def index():
    posts = Post.query.all()

    return render_template('index.html', posts=posts, current_time=datetime.utcnow())


#@main.ruote('/user')
#def user():





@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        #redirect(url_for())
    return render_template('index.html', form=form)


@main.route('/edit', methods=['GET', 'POST'])
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id=0):
    form = PostForm()
    if form.validate_on_submit():
        if id == 0:
            post = Post(author=current_user._get_current_object())
        else:
            post = Post.query.get(id)
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.post', id=post.id))
    return render_template('edit_post.html', form=form)


@main.route('/about')
def about():
    return render_template("about.html")


@main.route('/download/<filename>')
def download(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@main.route('/upload', methods=['GET', 'POST'])
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
    return render_template('upload.html', text=text)


@main.route('/attack')
@login_required
def attack():
    return render_template('attack.html')

# @main.app_template_filter('md')
# def markdown_to_html(txt):
#    from markdown import markdown
#    return markdown(txt)


# @main.app_template_test('current_link')
#    def is_current_link(href):
#    return href == request.path


# def read_md(filename):
#    from functools import reduce
#    with open(filename) as md_file:
#        # content = md_file.read()!
#        content = reduce(lambda x, y: x + y, md_file.readlines())
#    return content.encode('gbk').decode()


# @main.app_context_processor
# def inject():
#    return dict(read_md=read_md)
