2017-04-08
* 利用数据库 SQLAlchemy 建立表 Role, User。
* 合理化项目结构，添加蓝图。
* Bug：重整结构之后 nav.register_element 函数不能正常工作，在视图函数前加上蓝图名称解决，比如 index >> main.index。


2017-04-09
* 报错 no such table users，修改 data.sqlite 路径解决。
* To_be_solved：给 wtforms 表单设置默认值。
* 增加 register 表单和视图函数，可验证邮箱或用户名是否已被注册，规定了 email, name 的格式，若注册成功则录入数据库。
* 增加 login, logout 视图函数，具有登陆、退出功能。

2017-04-10
* 为了实现 login, logout 匹配不同的导航标签的功能，停用 flask_nav，改用 bootstrap 定义导航。
* 增加保护路由功能，只有登陆用户才能访问指定路由。
* To_be_solved：用户通过 email 或 username 均可登陆。
* Tips：初始化 FlaskForm 的子类的实例对象时，别忘了用()结尾。这是我的报错：TypeError: validate_on_submit() missing 1 required positional argument: 'self'。

2017-04-11
* 增加 flask-moment, flask-mail, 使用 qq 邮箱记得设置 MAIL_USE_SSL = True，而不是 MAIL_USE_TLS = True，说多了都是泪...
* 增加 tests 包。
* solved：用户通过 email 或 username 均可登陆。
* 增加 redirect(request.args.get('next')) 功能，重定向用户未登录前访问的页面。
* 增加 remember me 功能，保留用户 cookies。
* To_be_solved：关闭再打开浏览器进行认证会报错：The CSRF session token is missing。
* 增加密码散列功能。

2017-04-12
* 增加 confirmed 列，增加 register >> send_email (confirm | unconfirmed >> resend_confirmation) 确认账户功能，增加 before_request 视图函数过滤未确认的账户。
* 增加修改密码、重置密码、修改邮箱功能。与书中不同的是，验证账户、重置密码、修改邮箱这 3 个功能我使用了同一个安全令牌函数，后果尚待验证。
