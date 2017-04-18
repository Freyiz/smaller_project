import os
CDV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    CDV = coverage.coverage(branch=True, include='app/*')
    CDV.start()

from flask_migrate import Migrate, MigrateCommand, upgrade
from flask_script import Manager, Shell
from app import create_app, db
from app.models import User, Role, Post, Comment, Follow
from app.main.views import db_reset


def make_shell_context():
    return {'app': app, 'db': db, 'User': User, 'Follow': Follow, 'db_reset': db_reset,
            'Role': Role, 'Post': Post, 'Comment': Comment}

app = create_app('default')
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


if __name__ == '__main__':
    manager.run()
