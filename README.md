2017-04-08 (1a)
* 利用数据库 SQLAlchemy 建立表 Role, User。
* 合理化项目结构，添加蓝图。
* Bug：重整结构之后 nav.register_element 函数不能正常工作，在视图函数前加上蓝图名称解决，比如 index >> main.index。


2017-04-09 (1b)
* 报错 no such table users，修改 data.sqlite 路径解决。
* To_be_solved(q_1)：给 wtforms 表单设置默认值。
* 增加 register 表单和视图函数，可验证邮箱或用户名是否已被注册，规定了 email, name 的格式，若注册成功则录入数据库。
* 增加 login, logout 视图函数，具有登陆、退出功能。

2017-04-10 (1c)
* 为了实现 login, logout 匹配不同的导航标签的功能，停用 flask_nav，改用 bootstrap 定义导航。
* 增加保护路由功能，只有登陆用户才能访问指定路由。
* To_be_solved(q_2)：用户通过 email 或 username 均可登陆。
* Tips：初始化 FlaskForm 的子类的实例对象时，别忘了用()结尾。这是我的报错：TypeError: validate_on_submit() missing 1 required positional argument: 'self'。

2017-04-11 (1c)
* 增加 flask-moment, flask-mail, 使用 qq 邮箱记得设置 MAIL_USE_SSL = True，而不是 MAIL_USE_TLS = True，说多了都是泪...
* 增加 tests 包。
* solved(a_2)：用户通过 email 或 username 均可登陆。
* 增加 redirect(request.args.get('next')) 功能，重定向用户未登录前访问的页面。
* 增加 remember me 功能，保留用户 cookies。
* To_be_solved(q_3)：关闭再打开浏览器进行认证会报错：The CSRF session token is missing。
* 添加 password_hash 列。

2017-04-12 (1c)
* 增加 confirmed 列，增加 register >> send_email (confirm | unconfirmed >> resend_confirmation) 确认账户功能，增加 before_request 视图函数过滤未确认的账户。
* 增加修改密码、重置密码、修改邮箱功能。与书中不同的是，验证账户、重置密码、修改邮箱这 3 个功能我使用了同一个安全令牌函数，后果尚待验证。
* 增加 insert_roles() 方法，可初始化角色类别，增加角色和权限验证，增加两个自定义修饰器 permission_required(permission), admin_required(f)。
* 增加 ping() 方法，利用 before_app_request 刷新用户最后访问时间。

2017-04-13 (2a)
* 增加用户、管理员资料编辑器，利用 Gravatar 增加头像功能, 添加 avatar_hash 列。
* 增加首页显示所有博客文章和资料页显示个人博客文章功能。
* solved(a_1)：在视图函数添加 form.*.data == value 即可设置 * 显示为默认值 value。

2017-04-14 (2a)
* 增加分页功能。
* 增加博客文章页面，增加文章编辑功能。
* 增加关注功能，可查看关注者和被关注者，可在首页选择显示全部或者仅关注人的博客文章。

2017-04-15 (2a)
* 增加评论、管理评论功能，管理员可屏蔽或解除屏蔽不当评论。
* 增加 db_reset 测试函数，可重置数据库并生成相应的角色、用户、文章、评论和关注。
* To_be_solved(q_4)：上传头像功能，评论点赞功能，重定向相同页面后的滚动条处理。solved(a_4)：已解决。

2017-04-16 (2b)
* 增加基于 REST 的 API 蓝本。
* solved(a_3)：在相应的配置类中添加 WTF_CSRF_ENABLED = False 即可禁用 CSRF 保护。

2017-04-17 (2b)
* 增加测试客户端，增加 Web 程序和 Web 服务测试，增加基于 Selenium 的端到端测试。
* To_be_solved(q_5)：webdriver.Firefox() 无效，测试被 skipped。

2017-04-19 (2c)
* 增加评论点赞功能，评论排序的第一标准为点赞数（降序），第二标准为发表时间（升序）。

2017-04-20 (2c)
* 增加收藏文章功能。
* 增加修改头像功能。

2017-04-21 (2c)
* 改进 db_reset 测试函数，可生成点赞和收藏。
* 改进头像命名规则，解决之前上传头像后需要刷新才能正确显示新头像的 bug；遗留问题：用户的旧头像文件将保留在静态库。
* 增加 ALLOWED_EXTENSIONS 配置，限制头像上传格式。

2017-04-22 (3a)
* solved(a_5)：以 chrome 为例，在终端使用 sudo apt-get install chromium-chromedriver 命令，下载完成后 chromedriver 的默认路径为 /usr/lib/chromium-browser/chromedriver，将此路径作为参数传给 webdriver.Chrome() 即可。
* to_be_solved(q_6)：关于 flask-babel 的扩展使用。

2017-04-24 (3b)
* 部署到 heroku：一顿折腾，以下为坑：
    * heroku addons:add heroku-postgresql:dev 无效，替换为 heroku addons:create heroku-postgresql:hobby-dev，这两者据说是付费与免费的区别。
    * git push heroku master 失败：
        * 需要 buildpacks：程序文件夹根目录必须有 requirement.txt, Procfile, *.py 这三个文件，严格来说是远程仓库对应 repository 根目录下必须有这三个文件，因为其实只需要一个 .git 文件夹就可以 push 了。还有一个可选的 runtime.txt, 这个文件标明了 heroku 使用哪个版本的编程语言。注意 Procfile 文件名区分大小写，其内容也严格限制了空格的使用，比如我的是这样：web: gunicorn manage:app。
        * failed to detect app...：其实还是上一个问题，把本地的改动同步到远程仓库的 master 分支就可以了。
        * 详见 heroku 官方文档：https://devcenter.heroku.com/articles/buildpacks。
    * 各种 error pages，查看 heroku logs，google it。
    * Internal Server Error：若有关数据库的页面都打不开，而其他页面却能打开，说明数据库配置不正确。比如我之前用的是 sqlite，在 heroku 改用 postgresql，就要使用对应数据库的 URL。
        * 如果使用 SQLAlchemy,确保 SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or...， DATABASE_URL 从 heroku 的环境变量读取。
        * 把 models 模块里所有的 db.DateTime() 更换为 db.TIMESTAMP()，因为 postgresql 不支持 datetime 类型。
    * 部署完成之后若想使用静态库，记得更换对应路径，比如 UPLOAD_FOLDER = 'app/static/uploads'。
    * 本地调试记得设置 DEBUG=True。

2017-04-26 (3b)
* 增加注册验证码。利用 repatcha 为程序添加验证码很方便：
    * 用 google 注册 repatcha ,你会看到一个简单的教程。我没有按教程来，只复制了公钥和私钥。
    * 在 config 中添加 RECAPTCHA_PUBLIC_KEY = <你的公钥>, RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')，在环境变量中设置私钥。
    * 在对应表单中添加 recaptcha = RecaptchaField()，记得从 flask_wtf 导入 RecaptchaField。
    * 开始使用 google 验证吧！

2017-05-06 (3b)
* 增加登录验证码。利用 PIL 生成简单的随机字母验证码。
* 改进重置密码功能，登录用户和匿名用户均可重置密码。

2017-05-09 (3b)
* 添加网站图标，从 wow copy 过来的...
* 引入样式 font awesome，有各式图标可供选择。
* 利用 AJAX 实现 Single Page Applications，即页面局部刷新。使用类似 $.getJSON or $.post 这样的函数实现前后端交互。具体参考 http://flask.pocoo.org/docs/0.12/patterns/jquery/ 和 https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-ajax。

2017-05-10 (3b)
* 引入样式 notification，有各式 flask 消息可供选择。

2017-05-10 (3b)
* 改进导航条，当滚动条上滚时显示导航条。

2017-05-20 (3b)
* 完善注册程序，花了我十天...

2017-05-29 (3b)
* 增加晋升系统。
* 添加音效。

2017-06-01 (3b)
* 添加视频。

2017-06-04 (3b)
* 解决 heroku 的 500M 限制问题：新建另外一个域名，将视频上传到该网站。主站引用该网站的视频。每个heroku 账号可免费建立 5 个域名。
* 针对国内访问 heroku 存在延迟的问题，增加优酷模式，改善观看视频体验。
* 将大段 javascript 代码转入对应 js 文件再引用，增加网页加载效率。
* 增加点击到顶功能。

2017-06-05 (3b)
* 增加文本点击展开功能。

2017-06-06 (3b)
* 增加文章、评论、用户列表的多样排序功能。
* 增加分页页码指定框。

2017-06-07 (3b)
* to_be_solved(q_7)：添加视频到网站问题，视频放在哪里比较合适呢？放优酷有广告，放静态文件夹太占空间，放免费的 heroku 网速慢，而且各浏览器对视频格式、元素标签的标准也不统一，比如 chrome 可能不支持 embed 的 allowScriptAccess 等等。

2017_06_08 (3b)
* 关于 validate_on_submit()：如果一个视图函数里有多个 validate_on_submit()，一定要记得建立表单类时在 Field 后面设置 validators。
* 使用 jquery 修改 css 样式后 hover 失效：在 hover 样式的每条语句后面加上 !important 解决。 

2017_06_12 (3b)
* 增加用户，评论，文章的搜索功能。根据对应关键词搜索相关结果。

2017_06_15 (3b)
* 增加搜索结果高亮功能。

2017_06_19 (3b)
* 增加网站 footer。

2017_06_20 (3b)
* 修改文章表格 css。

2017_06_22 (3b)
* JS 中数组的拷贝有深浅之分，浅拷贝使用 = 即可，实际为一个对象，深拷贝使用 arrayObj.slice(start, [end]) 或 arrayObject.concat(arrayX,arrayX,......,arrayX)，实际为两个对象。
* 阻止二次点击事件： var t = 0; if (t === 1) { return false; } else { t = 1 }。


学习编程的个人经验
* google 是个好工具。
* 出了问题，想知道为什么？除了 google，你还可以翻看相应的原始文档或官方文档，如果你想得到最直接，最全面的答案。
* 学习编程是学习英语的良好机会。不想学英语？除非你能做到让大部分程序员都使用你的语言。
* 哲学是个好东西。你说你已经三十岁了，之前从没接触过编程，也不认识任何一个程序员，没有人能给你提供帮助，英语只会简单的点头 yes 摇头 no？没关系，哲学能帮到你——量变可以引发质变。我们都清楚这句话是什么意思。下面我分两点来作进一步的解释：
    * 改变是困难的，确实如此。但是，改变，任何时候都不晚。你应该听说过一句话：种一棵树，最好的时间是十年前，其次是现在。
    * 量变到质变是一个漫长的过程。比如，一个婴儿如果想长出长胡子，怎么办呢？我有一个办法——只要他坚持活到六十岁，就不难达到目标。幸好，我们从零开始到成为一个初级程序员并不需要六十年这么久，对吧？关键在于坚持，坚持啊，霞姨！
    
* 待处理：微信，新浪微博登录，第三方登录帐号绑定，部署到 sae，未验证用户引用不了外部 css，保存用户上传文件，消息定时消失