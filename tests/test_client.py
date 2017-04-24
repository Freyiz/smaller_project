# coding=utf-8
import unittest
from app import create_app, db
from app.models import User, Role
from flask import url_for


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue('旅行者' in response.get_data(as_text=True))

    def test_register_and_login(self):
        response = self.client.post(url_for('auth.register'), data={
            'email': '1@qq.com',
            'username': 'w1',
            'password': 'a123456',
            'password2': 'a123456'
        })
        self.assertTrue(response.status_code == 302)

        response = self.client.post(url_for('auth.login'), data={
            'username_or_email': '1@qq.com',
            'password': 'a123456'
        }, follow_redirects=True)
        self.assertTrue(b'w1' in response.data)

        response = self.client.get(url_for('auth.unconfirmed'))
        self.assertTrue('干点啥之前，请验证你的账户哦！' in response.get_data(as_text=True))

        user = User.query.filter_by(email='1@qq.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        self.assertTrue('验证成功' in response.get_data(as_text=True))

        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertTrue('See you again' in response.get_data(as_text=True))
