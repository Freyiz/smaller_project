from flask import render_template, request, jsonify, redirect, \
    url_for, flash, current_app, abort, make_response, session
from .forms import PostForm, CommentForm, EditProfileForm, \
    EditProfileAdminForm, RecaptchaForm, DemotionForm, JumpForm, SearchForm
from ..decorators import admin_required, permission_required
from ..models import Post, Comment, User, Role, Permission, Follow
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from datetime import datetime
from sqlalchemy import and_, or_
from . import main
from .. import db
import os


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
        flash('新公告已发布！')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    form_jump = JumpForm()
    if form_jump.validate_on_submit():
        page = form_jump.page_num.data
        return redirect(url_for('.index', page=page))
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, form_jump=form_jump,
                           posts=posts, pages=pagination.pages, pagination=pagination)


@main.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    email_address = '#'
    if current_user.email:
        email_address = 'http://mail.%s' % current_user.email.rsplit('@')[-1]
    page = request.args.get('page', 1, type=int)
    form_jump = JumpForm()
    if form_jump.validate_on_submit():
        page = form_jump.page_num.data
        return redirect(url_for('.user', page=page, username=username))
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, form_jump=form_jump, posts=posts,
                           pagination=pagination, pages=pagination.pages,
                           email_address=email_address)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        f = form.avatar.data
        filename = '%d_%s.%s' % (current_user.id,
                                 datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S'),
                                 f.filename.rsplit('.')[1])
        # filename = '%d.%s' % (current_user.id, f.filename.rsplit('.')[1])
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


@main.route('/promote/<id>', methods=['GET', 'POST'])
@login_required
def promote(id):
    user = User.query.get_or_404(id)
    if current_user != user:
        abort(404)
    if user.can(Permission.MODERATE_COMMENTS):
        form = DemotionForm()
        if form.validate_on_submit():
            user.role = Role.query.filter_by(name='民众').first()
            db.session.add(user)
            flash('神接受了你的忏悔。')
            return redirect(url_for('.index'))
        return render_template('promote_result.html', user=user, form=form,
                               result='demotion', title='忏悔之路')
    form = RecaptchaForm()
    if form.validate_on_submit():
        user.role = Role.query.filter_by(name='官员').first()
        db.session.add(user)
        return render_template('promote_result.html', user=user, result='promote', title='晋升之路')
    return render_template('promote.html', user=user, form=form)


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
        post.comments_count += 1
        db.session.add(comment)
        db.session.add(post)
        return redirect(url_for('.post', id=id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments_count - 1) // current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    form_jump = JumpForm()
    if form_jump.validate_on_submit():
        page = form_jump.page_num.data
        return redirect(url_for('.post', page=page, id=id))
    pagination = post.comments.order_by(Comment.likes.desc(), Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post.html', form=form, form_jump=form_jump, posts=[post],
                           comments=comments, pagination=pagination, pages=pagination.pages)


@main.route('/collect-toggle')
@login_required
def collect_toggle():
    id = request.args.get('id', type=int)
    post = Post.query.get_or_404(id)
    current_user.collect_toggle(post)
    return jsonify(result=post.collects)


@main.route('/made-post', methods=['GET', 'POST'])
@login_required
def made_post():
    id = request.args.get('id', 0, type=int)
    user_id = request.args.get('user_id', 0, type=int)
    user = User.query.get(user_id)
    form = PostForm()
    title = '变更公告：'
    if id:
        post = Post.query.get_or_404(id)
        if current_user != post.author and not current_user.is_administrator():
            abort(403)
        if form.validate_on_submit():
            post.body = form.body.data
            db.session.add(post)
            flash('公告已更改！')
            return redirect(url_for('.post', id=post.id))
        form.body.data = post.body
    else:
        title = '新公告'
        if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
            post = Post(body=form.body.data, author=current_user._get_current_object())
            db.session.add(post)
            flash('新公告已发布！')
            return redirect(url_for('.index'))
    return render_template('made_post.html', form=form, title=title, user=user)


@main.route('/edit-comment/<int:id>')
@login_required
def delete_comment(id):
    page = request.args.get('page', 1, type=int)
    comment = Comment.query.get_or_404(id)
    post = Post.query.get_or_404(comment.post_id)
    if current_user != comment.author:
        abort(403)
    post.comments_count -= 1
    db.session.add(post)
    db.session.delete(comment)
    flash('删除成功！')
    return redirect(url_for('.post', id=comment.post_id, page=page))


@main.route('/users', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def users():
    # 获得 title 和 query
    title = '英雄榜'
    query = User.query
    accord = request.args.get('accord', '角色名', type=str)
    keywords = request.args.get('keywords', '', type=str)
    keywords_list = keywords.split(' ')
    if keywords:
        if accord == '角色名':
            query = User.query.filter(and_(User.username.contains(keyword) for keyword in keywords_list))
        elif accord == '阵营':
            query = User.query.filter(and_(User.wow_faction.contains(keyword) for keyword in keywords_list))
        elif accord == '种族':
            query = User.query.filter(and_(User.wow_race.contains(keyword) for keyword in keywords_list))
        else:
            query = User.query.filter(and_(User.wow_class.contains(keyword) for keyword in keywords_list))
        title = '英雄榜：' + str(query.count()) + ' 个结果'

    # 获得 sort
    sort = request.args.get('sort', 're_id', type=str)
    if sort == 're_id':
        order = User.id.desc()
    elif sort == 'username':
        order = User.username.asc()
    elif sort == 're_username':
        order = User.username.desc()
    elif sort == 'wow_faction':
        order = User.wow_faction.asc()
    elif sort == 're_wow_faction':
        order = User.wow_faction.desc()
    elif sort == 'wow_race':
        order = User.wow_race.asc()
    elif sort == 're_wow_race':
        order = User.wow_race.desc()
    elif sort == 'wow_class':
        order = User.wow_class.asc()
    elif sort == 're_wow_class':
        order = User.wow_class.desc()
    elif sort == 'location':
        order = User.location.asc()
    elif sort == 're_location':
        order = User.location.desc()
    elif sort == 'followed':
        order = User.followed_count.asc()
    elif sort == 're_followed':
        order = User.followed_count.desc()
    elif sort == 'followers':
        order = User.followers_count.asc()
    elif sort == 're_followers':
        order = User.followers_count.desc()
    elif sort == 'role_id':
        order = User.role_id.asc()
    elif sort == 're_role_id':
        order = User.role_id.desc()
    elif sort == 'confirmed':
        order = User.confirmed.asc()
    elif sort == 're_confirmed':
        order = User.confirmed.desc()
    elif sort == 'member_since':
        order = User.member_since.asc()
    elif sort == 're_member_since':
        order = User.member_since.desc()
    elif sort == 'last_seen':
        order = User.last_seen.asc()
    elif sort == 're_last_seen':
        order = User.last_seen.desc()
    else:
        order = User.id.asc()

    # 页面自定义搜索
    form_jump = JumpForm()
    if form_jump.validate_on_submit():
        page = form_jump.page_num.data
        return redirect(url_for('.users', page=page, sort=sort, accord=accord, keywords=keywords))

    # 关键词查找 user
    form_search = SearchForm()
    if form_search.validate_on_submit():
        keywords = form_search.keywords.data
        return redirect(url_for('.users', sort=sort, accord=session['accord'], keywords=keywords))
    form_search.keywords.data = keywords

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(order).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    users = pagination.items
    return render_template('users.html', form_jump=form_jump, form_search=form_search,
                           pages=pagination.pages, users=users, title=title, sort=sort,
                           pagination=pagination, keywords=keywords, accord=accord)


@main.route('/comments', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comments():
    # 获得 title 和 query
    title = '议政厅'
    query = Comment.query
    accord = request.args.get('accord', '内容', type=str)
    keywords = request.args.get('keywords', '', type=str)
    keywords_list = keywords.split(' ')
    if keywords:
        if accord == '内容':
            query = Comment.query.filter(and_(Comment.body.contains(keyword) for keyword in keywords_list))
        else:
            users = User.query.filter(and_(User.username.contains(keyword) for keyword in keywords_list)).all()
            if users:
                query = Comment.query.filter(or_(Comment.author_id.contains(user.id) for user in users))
            else:
                query = Comment.query.filter_by(id=-1)
        title = '议政厅：' + str(query.count()) + ' 个结果'

    # 获得 sort
    sort = request.args.get('sort', 're_timestamp', type=str)
    if sort == 're_timestamp':
        order = Comment.timestamp.desc()
    elif sort == 'likes':
        order = Comment.likes.asc()
    elif sort == 're_likes':
        order = Comment.likes.desc()
    elif sort == 'username':
        order = Comment.author_username.asc()
    elif sort == 're_username':
        order = Comment.author_username.desc()
    else:
        order = Comment.timestamp.asc()

    # 页面自定义搜索
    form_jump = JumpForm()
    if form_jump.validate_on_submit():
        page = form_jump.page_num.data
        return redirect(url_for('.comments', page=page, sort=sort, accord=accord, keywords=keywords))

    # 关键词查找 comment
    form_search = SearchForm()
    if form_search.validate_on_submit():
        keywords = form_search.keywords.data
        return redirect(url_for('.comments', sort=sort, accord=session['accord'], keywords=keywords))
    form_search.keywords.data = keywords

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(order).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('comments.html', form_jump=form_jump, form_search=form_search,
                           pages=pagination.pages, comments=comments, title=title,
                           pagination=pagination, keywords=keywords, sort=sort, accord=accord)


@main.route('/follow-toggle')
@permission_required(Permission.FOLLOW)
def follow_toggle():
    id = request.args.get('id', type=int)
    user = User.query.filter_by(id=id).first_or_404()
    current_user.follow_toggle(user)
    if current_user.is_following(user):
        text = '取消追随'
    else:
        text = '追随'
    if user.followers.count() > 1:
        href = "/followers/" + user.username
    else:
        href = '#'
    return jsonify(result=user.followers.count() - 1, text=text, href=href)


@main.route('/followers/<username>', methods=['GET', 'POST'])
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    form_jump = JumpForm()
    if form_jump.validate_on_submit():
        page = form_jump.page_num.data
        return redirect(url_for('.followers', page=page, username=username))
    pagination = user.followers.order_by(Follow.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('follow.html', user=user, follows=follows, title='的追随者',
                           pages=pagination.pages, pagination=pagination,
                           endpoint='.followers', form_jump=form_jump)


@main.route('/followed-by/<username>', methods=['GET', 'POST'])
def followed_by(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    form_jump = JumpForm()
    if form_jump.validate_on_submit():
        page = form_jump.page_num.data
        return redirect(url_for('.followed_by', page=page, username=username))
    pagination = user.followed.order_by(Follow.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('follow.html', user=user, follows=follows, title='的追随',
                           pages=pagination.pages, pagination=pagination,
                           endpoint='.followed_by', form_jump=form_jump)


@main.route('/all')
def show_all():
    resp = make_response(redirect(url_for('.posts')))
    resp.set_cookie('show_which', 'all', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.posts')))
    resp.set_cookie('show_which', 'followed', max_age=30*24*60*60)
    return resp


@main.route('/collected')
@login_required
def show_collected():
    resp = make_response(redirect(url_for('.posts')))
    resp.set_cookie('show_which', 'collected', max_age=30*24*60*60)
    return resp


@main.route('/accord')
@login_required
def show_accord():
    accord = request.args.get('accord', type=str)
    session['accord'] = accord
    return jsonify()


@main.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    # 获得 title 和 query
    title = '所有公告'
    query = Post.query
    accord = request.args.get('accord', '内容', type=str)
    keywords = request.args.get('keywords', '', type=str)
    keywords_list = keywords.split(' ')
    show_which = request.cookies.get('show_which', 'all', type=str)
    if keywords:
        if accord == '内容':
            query = Post.query.filter(and_(Post.body.contains(keyword) for keyword in keywords_list))
        else:
            users = User.query.filter(and_(User.username.contains(keyword) for keyword in keywords_list)).all()
            if users:
                query = Post.query.filter(or_(Post.author_id.contains(user.id) for user in users))
            else:
                query = Post.query.filter_by(id=-1)
        title = '公告：' + str(query.count()) + ' 个结果'
    else:
        if show_which == 'followed':
            title = '我的追随'
            query = current_user.posts_followed
        if show_which == 'collected':
            title = '我的收藏'
            query = current_user.posts_collected

    # 获得 sort
    sort = request.args.get('sort', 're_timestamp', type=str)
    if sort == 're_timestamp':
        order = Post.timestamp.desc()
    elif sort == 'comments_count':
        order = Post.comments_count.asc()
    elif sort == 're_comments_count':
        order = Post.comments_count.desc()
    elif sort == 'collects':
        order = Post.collects.asc()
    elif sort == 're_collects':
        order = Post.collects.desc()
    elif sort == 'username':
        order = Post.author_username.asc()
    elif sort == 're_username':
        order = Post.author_username.desc()
    else:
        order = Post.timestamp.asc()
    order2 = Post.timestamp.desc()

    # 页面自定义搜索
    form_jump = JumpForm()
    if form_jump.validate_on_submit():
        page = form_jump.page_num.data
        return redirect(url_for('.posts', page=page, sort=sort, accord=accord, keywords=keywords))

    # 关键词查找 post
    form_search = SearchForm()
    if form_search.validate_on_submit():
        keywords = form_search.keywords.data
        return redirect(url_for('.posts', sort=sort, accord=session['accord'], keywords=keywords))
    form_search.keywords.data = keywords

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(order, order2).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('posts.html', form_jump=form_jump, form_search=form_search,
                           pages=pagination.pages, posts=posts, show_which=show_which,
                           title=title, pagination=pagination, keywords=keywords,
                           sort=sort, accord=accord)


@main.route('/like-toggle')
@login_required
def like_toggle():
    id = request.args.get('id', type=int)
    comment = Comment.query.get_or_404(id)
    current_user.like_toggle(comment)
    if comment not in current_user.comments_like.all():
        text = 'fa fa-thumbs-o-up'
    else:
        text = 'fa fa-thumbs-up'
    return jsonify(result=comment.likes, text=text)


@main.route('/comment-display-toggle')
@permission_required(Permission.MODERATE_COMMENTS)
def comment_display_toggle():
    id = request.args.get('id', type=int)
    comment = Comment.query.get_or_404(id)
    if comment.disabled:
        comment.disabled = False
        result = '屏蔽'
        text = 'btn btn-success btn-xs'
    else:
        comment.disabled = True
        result = '显示'
        text = 'btn btn-danger btn-xs'
    db.session.add(comment)
    return jsonify(result=result, text=text)


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return '服务器即将关闭...'


@main.route('/wow-memory')
def wow_memory():
    return render_template("wow_memory.html")


@main.route('/tavern')
def tavern():
    return render_template("tavern.html")


@main.route('/license')
def license():
    return render_template('license.html')
