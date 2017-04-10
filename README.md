2017-04-08
* 利用数据库 SQLAlchemy 建立表 Role, User。
* 合理化项目结构，添加蓝图。
* BUG：重整结构之后 nav.register_element 函数不能正常工作，在视图函数前加上蓝图名称解决，比如 index >> main.index。


2017-04-09
* 报错 no such table users，修改 data.sqlite 路径解决。
* 未解决问题：给 wtforms 表单设置默认值。
* 增加 register 表单和视图函数，可验证邮箱或用户名是否已被注册，规定了 email, name 的格式，若注册成功则录入数据库。
* 增加 login, logout 视图函数，具有登陆、退出功能。
* 为了实现 login, logout 匹配不同的导航标签的功能，停用 flask_nav，改用 bootstrap 定义导航。
* 增加保护路由功能，只有登陆用户才能访问指定路由。