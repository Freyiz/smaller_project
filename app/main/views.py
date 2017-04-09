from flask import render_template, request, send_from_directory
from . import main
from ..config import Config
import os


@main.route('/')
def index():
    return render_template('index.html', text='<h1><i>Hello World!</i></h1>', body='## *火星人来过!*')


@main.route('/about')
def about():
    return render_template("about.html", img_path=r'%s\bg.jpg' % Config.UPLOAD_FOLDER)


@main.route('/attack')
def attack():
    return render_template('attack.html')


@main.route('/upload', methods=['GET', 'POST'])
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

