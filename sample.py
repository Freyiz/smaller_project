from flask import Flask, render_template, send_from_directory, flash, session
from flask_script import Manager
from flask_bootstrap import Bootstrap
from forms import NameForm
from flask_nav import Nav
from flask_nav.elements import *
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config.from_pyfile('config')
app.config['UPLOAD_FOLDER'] = r'D:\my_project\static\uploads'
manager = Manager(app)
bootstrap = Bootstrap(app)
nav = Nav()
nav.register_element('top', Navbar(
    'Welcome',
    View('主页', 'index'),
    View('登陆', 'login'),
    View('上传', 'upload'),
    View('进攻', 'attack'),
    View('关于', 'about'),
))
nav.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    return render_template('index.html', text='<h1><i>Hello World!</i></h1>', body='## *火星人来过!*')


@app.route('/about')
def about():
    return render_template("about.html", img_path=r'%s\bg.jpg' % app.config['UPLOAD_FOLDER'])


@app.route('/base')
def base():
    return render_template("base.html")


@app.route('/attack')
def attack():
    return render_template('attack.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = NameForm()
    flash('欢迎回来！')
    return render_template('login.html', title='登陆', form=form)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    text = ''
    if request.method == 'POST':
        f = request.files['file']
        if f:
            filename = f.filename
            if f.filename in os.listdir(app.config['UPLOAD_FOLDER']):
                text = '文件已存在！'
            else:
                text = '上传成功！'
            # secure_filename（） 不识别汉字的问题尚未解决
            # filename = secure_filename(f.filename)
            # if filename == 'py':
            # filename = '12345.py'
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('upload'), filename=filename)
        else:
            text = '未找到文件！'
    return render_template('upload.html', text=text)


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@manager.command
def dev():
    """reload when modification happened"""
    from livereload import Server
    live_server = Server(app.wsgi_app)
    live_server.watch('**/*.*')
    live_server.serve()


@app.template_filter('md')
def markdown_to_html(txt):
    from markdown import markdown
    return markdown(txt)


@app.template_test('current_link')
def is_current_link(href):
    return href == request.path


def read_md(filename):
    from functools import reduce
    import codecs
    with codecs.open(filename) as md_file:
        # content = md_file.read()!
        content = reduce(lambda x, y: x + y, md_file.readlines())
    return content.encode('gbk').decode()


@app.context_processor
def inject():
    return dict(read_md=read_md)

if __name__ == '__main__':
    manager.run()