# coding=utf-8
import unittest
from app.models import User, Role
from app import create_app, db
from flask import url_for, json
from base64 import b64encode


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, email, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (email + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_posts'), content_type='application/json')
        self.assertTrue(response.status_code == 200)

    def test_posts(self):
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='1@qq.com', password='a123456', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        response = self.client.post(url_for('api.new_post'),
                                    headers=self.get_api_headers('1@qq.com', 'a123456'),
                                    data=json.dumps({'body': '# 我是文章内容'}))
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        response = self.client.get(url, headers=self.get_api_headers('1@qq.com', 'a123456'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['body'] == '# 我是文章内容')
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body_html'] == '<h1>我是文章内容</h1>')