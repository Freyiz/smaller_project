from flask import render_template, send_from_directory
from config import Config
from . import main


@main.route('/')
def index():
    return render_template('index.html', text='<h1><i>Hello World!</i></h1>', body='## *火星人来过!*')


@main.route('/about')
def about():
    return render_template("about.html", img_path=r'%s\bg.jpg' % Config.UPLOAD_FOLDER)


@main.app_template_filter('md')
def markdown_to_html(txt):
    from markdown import markdown
    return markdown(txt)


#    @main.app_template_test('current_link')
#    def is_current_link(href):
#        return href == request.path


def read_md(filename):
    from functools import reduce
    with open(filename) as md_file:
        # content = md_file.read()!
        content = reduce(lambda x, y: x + y, md_file.readlines())
    return content.encode('gbk').decode()


@main.app_context_processor
def inject():
    return dict(read_md=read_md)


@main.route('/download/<filename>')
def download(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
