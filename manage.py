import os
CDV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    CDV = coverage.coverage(branch=True, include='app/*')
    CDV.start()

if os.path.exists('.env'):
    print('导入环境变量...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from flask_migrate import Migrate, MigrateCommand, upgrade
from flask_script import Manager, Shell
from app import create_app, db
from app.models import User, Role, Post, Comment, Follow


def make_shell_context():
    return {'app': app, 'db': db, 'User': User, 'Follow': Follow,
            'Role': Role, 'Post': Post, 'Comment': Comment}

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def dev():
    """reload when modification happened"""
    from livereload import Server
    live_server = Server(app.wsgi_app)
    live_server.watch('**/*.*')
    live_server.serve()


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if CDV:
        CDV.stop()
        CDV.save()
        print('Coverage 概要')
        CDV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        CDV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' %covdir)
        CDV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """在分析器模式下运行"""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """运行部署任务"""
    upgrade()
    Role.insert_roles()
    User.add_self_follows()


@manager.command
def reset():
    """重置数据库"""
    print('开始重置数据库...')
    print('清空数据库...')
    db.drop_all()
    print('创建数据库...')
    db.create_all()
    print('生成角色...')
    Role.insert_roles()
    print('生成我...')
    u = User(wow_faction='联盟', wow_race='暗夜精灵', wow_class='德鲁伊', username='Yiz', email='562124140@qq.com', password='1',
             confirmed=True, name='野蛮角斗士', location='试炼之环', about_me='非著名猫德')
    u2 = User(wow_faction='部落', wow_race='兽人', wow_class='萨满祭司', username='萨尔', email='181826029@qq.com', password='1',
              role=Role.query.filter_by(name='官员').first(), confirmed=True, name='神出鬼没的', location='奥格瑞玛', about_me='部落精神领袖，世界萨')
    u3 = User(username='冬泉信使', email='freyizg@gmail.com', password='1',
              role=Role.query.filter_by(name='官员').first(), confirmed=True, name='游荡的', location='冬泉谷', about_me='这封信上写的什么？')
    db.session.add_all((u, u2, u3))
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

    def generate_likes_and_collections():
        from random import randint
        for i in range(1000):
            u = User.query.get(randint(1, User.query.count()))
            u2 = User.query.get(randint(1, User.query.count()))
            c = Comment.query.get(randint(1, Comment.query.count()))
            p = Post.query.get(randint(1, Post.query.count()))
            if c not in u.comments_like:
                u.comments_like.append(c)
                c.likes += 1
                db.session.add(u)
            if p not in u2.posts_collected:
                u2.posts_collected.append(p)
                p.collects += 1
                db.session.add(u2)
                db.session.add(p)
        db.session.commit()

    print('生成点赞和收藏...')
    generate_likes_and_collections()
    print('重置数据库完成，谢谢使用!')
    quit()

if __name__ == '__main__':
    manager.run()
