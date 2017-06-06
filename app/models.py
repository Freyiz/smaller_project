import hashlib
from datetime import datetime
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from app.exceptions import ValidationError
from . import db, login_manager


users_like_comments = db.Table('likes',
                               db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                               db.Column('comment_id', db.Integer, db.ForeignKey('comments.id')))

users_collect_posts = db.Table('collections',
                               db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                               db.Column('post_id', db.Integer, db.ForeignKey('posts.id')))


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class WowConfig:
    factions = ['联盟', '部落']
    races = {
        '人类': '111011010111',
        '侏儒': '101011010111',
        '矮人': '111111010111',
        '暗夜精灵': '101011111101',
        '德莱尼': '111110010101',
        '狼人': '101011100111',
        '熊猫人': '100111010101',
        '兽人': '101111010110',
        '亡灵': '101011010111',
        '牛头人': '111110110001',
        '巨魔': '101111110111',
        '血精灵': '111011011111',
        '地精': '101110010111'
    }
    classes = ['战士', '圣骑士', '死亡骑士', '萨满祭司', '猎人', '盗贼', '德鲁伊', '武僧', '恶魔猎手', '法师', '术士', '牧师']
    basic = {
        '联盟': '#0078FF',
        '部落': '#B30000',
        '中立': '#ffa366',
        '死亡骑士': ['#C41F3B', 'death-knight'],
        '恶魔猎手': ['#A330C9', 'demon-hunter'],
        '德鲁伊': ['#FF7D0A', 'druid'],
        '猎人': ['#ABD473', 'hunter'],
        '法师': ['#69CCF0', 'mage'],
        '武僧': ['#00FF96', 'monk'],
        '圣骑士': ['#F58CBA', 'paladin'],
        '牧师': ['#FFFFFF', 'priest'],
        '盗贼': ['#FFF569', 'rogue'],
        '萨满祭司': ['#0070DE', 'shaman'],
        '术士': ['#9482C9', 'warlock'],
        '战士': ['#C79C6E', 'warrior']
    }

    def random_player(self):
        from random import choice

        wow_class = choice(self.classes)
        races_choice = []
        for race in self.races:
            if self.races[race][self.classes.index(wow_class)] == '1':
                races_choice.append(race)
        wow_race = choice(races_choice)
        if wow_race in ['人类', '矮人', '暗夜精灵', '侏儒', '德莱尼', '狼人']:
            wow_faction = '联盟'
        elif wow_race == '熊猫人':
            wow_faction = choice(self.factions)
        else:
            wow_faction = '部落'

        return wow_faction, wow_race, wow_class


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    default = db.Column(db.BOOLEAN, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            '民众': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            '官员': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, False),
            '神': (0xff, False)
        }
        for r in roles:
            if not Role.query.filter_by(name=r).first():
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.TIMESTAMP(), default=datetime.utcnow)

    @staticmethod
    def generate_fake(x=5, y=20):
        from random import randint

        for user in User.query.all():
            for i in range(randint(x, y)):
                u = randint(1, User.query.count())
                if not user.is_following(User.query.get(u)):
                    follow = Follow(follower=user, followed=User.query.get(u))
                    db.session.add(follow)
        db.session.commit()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    wow_faction = db.Column(db.String())
    wow_race = db.Column(db.String())
    wow_class = db.Column(db.String())
    wow_avatar = db.Column(db.String())
    faction_color = db.Column(db.String())
    class_color = db.Column(db.String())
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar_hash = db.Column(db.String(32))
    avatar = db.Column(db.String())
    confirmed = db.Column(db.BOOLEAN, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    last_seen = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')
    comments_like = db.relationship('Comment',
                                    secondary=users_like_comments,
                                    backref=db.backref('users_like', lazy='dynamic'),
                                    lazy='dynamic')
    posts_collected = db.relationship('Post',
                                    secondary=users_collect_posts,
                                    backref=db.backref('users_collect', lazy='dynamic'),
                                    lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.role:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email and not self.avatar_hash:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.followers.append(Follow(follower=self))
        if not self.wow_faction:
            self.wow_faction = '中立'
            self.wow_race = '食人魔'
            self.wow_class = '战士'
        self.faction_color = WowConfig.basic[self.wow_faction]
        self.class_color = WowConfig.basic[self.wow_class][0]
        self.wow_avatar = '../static/wow/class/' + WowConfig.basic[self.wow_class][1] + '.jpg'

    def __repr__(self):
        return '<User %r>' % self.username

    def can(self, permissions):
        return (self.role is not None) and (self.role.permissions & permissions == permissions)

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise AttributeError('呵呵')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if not new_email:
            return False
        if self.query.filter_by(email=new_email).first():
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts', id=self.id, _external=True),
            'post_count': self.posts.count(),
        }
        return json_user

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
        db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def follow_toggle(self, user):
        if self.is_following(user):
            self.unfollow(user)
        else:
            self.follow(user)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def like_toggle(self, comment):
        if comment not in self.comments_like.all():
            self.comments_like.append(comment)
            comment.likes += 1
            db.session.add(comment)
        else:
            self.comments_like.remove(comment)
            comment.likes -= 1
            db.session.add(comment)

    def collect_toggle(self, post):
        if post not in self.posts_collected.all():
            self.posts_collected.append(post)
            post.collects += 1
            db.session.add(post)
        else:
            self.posts_collected.remove(post)
            post.collects -= 1
            db.session.add(post)

    @property
    def posts_followed(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    @staticmethod
    def generate_fake(count=100):
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            player = WowConfig().random_player()
            new_name = forgery_py.internet.user_name()
            if not User.query.filter_by(username=new_name).first():
                u = User(wow_faction=player[0],
                         wow_race=player[1],
                         wow_class=player[2],
                         email=forgery_py.internet.email_address(),
                         username=new_name,
                         password=forgery_py.lorem_ipsum.word(),
                         name=forgery_py.name.full_name(),
                         location=forgery_py.address.city(),
                         about_me=forgery_py.lorem_ipsum.sentence(),
                         member_since=forgery_py.date.date(True))
                db.session.add(u)
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP(), default=datetime.utcnow, index=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    comments_count = db.Column(db.Integer, default=0, index=True)
    collects = db.Column(db.Integer, default=0, index=True)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            post = Post(body=forgery_py.lorem_ipsum.sentences(randint(5, 30)),
                        timestamp=forgery_py.date.date(True),
                        author=u)
            db.session.add(post)
        db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count(),
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if not body or body == '':
            raise ValidationError('没有内容')
        return Post(body=body)

db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP(), default=datetime.utcnow, index=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    disabled = db.Column(db.Boolean)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    likes = db.Column(db.Integer, default=0, index=True)

    @staticmethod
    def generate_fake(x=5, y=15):
        from random import randint
        import forgery_py

        for post in Post.query.all():
            for i in range(randint(x, y)):
                u = randint(1, User.query.count())
                comment = Comment(body=forgery_py.lorem_ipsum.sentence(),
                                  author=User.query.get(u),
                                  post=post)
                post.comments_count += 1
                db.session.add(comment)
                db.session.add(post)
        db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code',
                        'em', 'i', 'strong', ]
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if not body or body == '':
            raise ValidationError('没有内容')
        return Comment(body=body)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)
