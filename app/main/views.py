# coding=utf-8
from flask import render_template, send_from_directory, request, \
    redirect, url_for, flash, current_app, abort, make_response
from . import main
from flask_login import login_required, current_user
import os
from .forms import PostForm, CommentForm, EditProfileForm, EditProfileAdminForm
from ..models import Post, Comment, User, Role, Permission
from .. import db
from ..decorators import admin_required, permission_required
from flask_sqlalchemy import get_debug_queries
from datetime import datetime


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
    show_which = request.cookies.get('show_which', 'all')
    query = Post.query
    if current_user.is_authenticated:
        if show_which == 'followed':
            query = current_user.followed_posts
        if show_which == 'collection':
            query = current_user.posts_collect
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_which=show_which, pagination=pagination)


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
        f = form.avatar.data
        filename = '%d_%s.%s' % (current_user.id,
                                 datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S'),
                                 f.filename.rsplit('.')[1])
        current_user.avatar = os.path.join('../static/uploads', filename)
        f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
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
    pagination = post.comments.order_by(Comment.likes.desc(), Comment.timestamp.asc()).paginate(
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
    current_user.follow_toggle(user)
    return redirect(url_for('.user', username=user.username))


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
    resp.set_cookie('show_which', 'all', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_which', 'followed', max_age=30*24*60*60)
    return resp


@main.route('/collection')
@login_required
def show_collection():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_which', 'collection', max_age=30*24*60*60)
    return resp


@main.route('/like/<int:id>')
@login_required
def like_toggle(id):
    page = request.args.get('page', 1, type=int)
    comment = Comment.query.get_or_404(id)
    current_user.like_toggle(comment)
    return redirect(url_for('.post', id=comment.post_id, page=page))


@main.route('/collect/<int:id>')
@login_required
def collect_toggle(id):
    page = request.args.get('page', 1, type=int)
    post = Post.query.get_or_404(id)
    current_user.collect_toggle(post)
    return redirect(url_for('.index', id=id, page=page))


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return '服务器即将关闭...'


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    text = ''
    if request.method == 'POST':
        f = request.files['file']
        if f:
            filename = f.filename
            if f.filename in os.listdir(current_app.config['UPLOAD_FOLDER']):
                text = '文件已存在！'
            else:
                text = '上传成功！'
            # secure_filename（） 不识别汉字的问题尚未解决
            # filename = secure_filename(f.filename)
            # if filename == 'py':
            # filename = '12345.py'
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('upload'), filename=filename)
        else:
            text = '未找到文件！'
    return render_template('upload.html', text=text)


@main.route('/download/<filename>')
def download(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


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
import os
from app import oauth
from flask import session

#if os.path.exists('.env'):
#    for line in open('.env'):
#        var = line.strip().split('=')
#        if len(var) == 2 and var[0].startswith('REN2'):
#            os.environ[var[0]] = var[1]

ren2_id = os.environ.get('REN2_APP_ID', '483347')
ren2_key = os.environ.get('REN2_APP_KEY', 'cd896ffc91cd43459a7f2eaebe92be1d')

ren2 = oauth.remote_app(
    'ren2',
    consumer_key=ren2_id,
    consumer_secret=ren2_key,
    base_url='https://graph.renren.com',
    request_token_url=None,
    access_token_url='/oauth/token',
    authorize_url='/oauth/authorize'
)


@main.route('/user-info')
def get_user_info():
    if 'ren2_token' in session:
        return redirect(session['user']['avatar'][0]['url'])
    return redirect(url_for('.ren2_login'))


@main.route('/ren2-login')
def login():
    return ren2.authorize(callback=url_for('.ren2_authorized', _external=True))


@main.route('/ren2-authorized')
def ren2_authorized():
    resp = ren2.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['ren2_token'] = (resp['access_token'], '')

    # Get openid via access_token, openid and access_token are needed for API calls
    if isinstance(resp, dict):
        session['user'] = resp.get('user')
    return redirect(url_for('.get_user_info'))


@ren2.tokengetter
def get_ren2_token():
    return session.get('ren2_token')
