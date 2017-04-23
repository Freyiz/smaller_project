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
* To_be_solved(q_4)：上传头像功能、评论点赞功能、重定向相同页面后的滚动条处理。

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

2017-04-21 (3a)
* solved(a_5)：以 chrome 为例，在终端使用 sudo apt-get install chromium-chromedriver 命令，下载完成后 chromedriver 的默认路径为 /usr/lib/chromium-browser/chromedriver，将此路径作为参数传给 webdriver.Chrome() 即可。
* to_be_solved(q_6)：关于 flask-babel 的扩展使用。
