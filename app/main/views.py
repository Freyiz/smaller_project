from flask import render_template, send_from_directory, request, \
    redirect, url_for, flash, current_app, abort, make_response
from . import main
from flask_login import login_required, current_user
from config import Config
import os
from .forms import PostForm, CommentForm, EditProfileForm, EditProfileAdminForm
from ..models import Post, Comment, User, Role, Permission, Follow
from .. import db
from ..decorators import admin_required, permission_required
from flask_sqlalchemy import get_debug_queries


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                '树懒查询: %s\n参数: %s\n耗时: %fs\n上下文: %s\n' %
                (query.statement, query.parameters, query.duration, query.context))
    return response


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('信息修改成功！')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.email = form.email.data
        user.username = form.username.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('信息修改成功！')
        return redirect(url_for('.user', username=user.username))
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.email.data = user.email
    form.username.data = user.username
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.is_administrator():
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.COMMENT)
def post(id):
    post = Post.query.get(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post.html', form=form, posts=[post], page=page,
                           comments=comments, pagination=pagination)


@main.route('/edit-comment/<int:id>')
@login_required
def delete_comment(id):
    page = request.args.get('page', 1, type=int)
    comment = Comment.query.get_or_404(id)
    if current_user != comment.author:
        abort(403)
    db.session.delete(comment)
    return redirect(url_for('.post', id=comment.post_id, page=page))


@main.route('/moderate')
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('moderate.html', page=page, pagination=pagination, comments=comments)


@main.route('/comment-show-toggle/<int:id>')
@permission_required(Permission.MODERATE_COMMENTS)
def comment_show_toggle(id):
    page = request.args.get('page', 1, type=int)
    comment = Comment.query.get_or_404(id)
    if comment.disabled:
        comment.disabled = False
    else:
        comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.post', id=comment.post_id, page=page))


@main.route('/follow/<username>')
@permission_required(Permission.FOLLOW)
def follow_toggle(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        current_user.unfollow(user)
    else:
        current_user.follow(user)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, follows=follows, title='的关注者',
                           pagination=pagination, endpoint='.followers')


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, follows=follows, title='的关注',
                           pagination=pagination, endpoint='.followed_by')


@main.route('/all')
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


# @main.route('/shutdown')
# def server_shutdown():
#    if not current_app.testing:
#        abort(404)
#    shutdown = request.environ.get('werkzeug.server.shutdown')
#    if not shutdown:
#        abort(500)
#    shutdown()
#    return '服务器即将关闭...'


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


@main.route('/download/<filename>')
def download(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@main.route('/attack')
@login_required
def attack():
    return render_template('attack.html')


@main.route('/about')
def about():
    return render_template("about.html")


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

def db_reset():
    print('开始重置数据库...')
    print('清空数据库...')
    db.drop_all()
    print('创建数据库...')
    db.create_all()
    print('生成角色...')
    Role.insert_roles()
    print('生成我...')
    u = User(username='Yiz', email='562124140@qq.com', password='1', confirmed=True, name='野蛮角斗士',
             location='试炼之环', about_me='非著名猫德')
    db.session.add(u)
    db.session.commit()
    print('生成小弟...')
    User.generate_fake(200)
    print('生成文章...')
    Post.generate_fake(200)
    print('生成评论...')
    Comment.generate_fake(5, 15)
    print('生成关注...')
    Follow.generate_fake(5, 20)
    print('生成自关注...')
    User.add_self_follows()
    print('重置数据库完成，谢谢使用!')
    quit()
