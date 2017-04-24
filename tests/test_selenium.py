# coding=utf-8
from selenium import webdriver
import unittest
from app.models import User, Role, Post, Comment, Follow
from app import create_app, db
import threading


class SeleniumTestCase(unittest.TestCase):
    client = None
    app_context = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.client = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
        except:
            pass

        if cls.client:
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)
            Comment.generate_fake(3, 5)
            Follow.generate_fake(3, 5)

            admin_role = Role.query.filter_by(name='Administrator').first()
            admin = User(role=admin_role, email='1@qq.com', username='w1',
                         password='a123456', confirmed=True)
            db.session.add(admin)
            db.session.commit()

            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            db.drop_all()
            db.session.remove()
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('浏览器不可用')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        self.client.get('http://localhost:5000/')
        self.assertTrue('旅行者' in self.client.page_source)

        self.client.find_element_by_link_text('登陆').click()
        self.assertTrue('<h1>登录</h1>' in self.client.page_source)

        self.client.find_element_by_name('username_or_email').send_keys('1@qq.com')
        self.client.find_element_by_name('password').send_keys('a123456')
        self.client.find_element_by_name('submit').click()
        self.assertTrue('w1' in self.client.page_source)

        self.client.find_element_by_link_text('账户').click()
        self.client.find_element_by_link_text('个人信息').click()
        self.assertTrue('更改信息' in self.client.page_source)

