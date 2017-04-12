from flask_migrate import Migrate, MigrateCommand, upgrade
from flask_script import Manager, Shell
from app import create_app, db
from app.models import User, Role, Post, Comment
from app.email import send_email


def make_shell_context():
    return {'app': app, 'db': db, 'User': User, 'send_mail': send_email,
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
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


# @manager.command
# def deploy():
#    from app.models import Role
#    Role.seed()
#    upgrade()

if __name__ == '__main__':
    manager.run()
