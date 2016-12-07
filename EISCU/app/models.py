from sqlalchemy import Column,Integer, String
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import current_user,UserMixin,AnonymousUserMixin
from app import db,login_manager
from datetime import datetime
#生成头像url
from flask import request,current_app
import hashlib
# 获取当前项目路径 
# 处理markdown
from markdown import markdown
import bleach



class Follow(db.Model):
    __tablename__='follows'
    # 用户
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    # 关注的人
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    follow_date = db.Column(db.DateTime,default=datetime.utcnow)


# 用户类 数据表字段包括 ： id, 用户名，邮箱，密码哈希值，真实名字，关于说明，注册日期，最近登录日期，地址，邮件确认是否成功，
#       外键有： 文章表格，角色表格id, 评论
class User(UserMixin,db.Model):
    __tablename__='users'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    password_hash = db.Column(db.String(128),nullable=False)
    # nickname = db.Column(db.String(80))
    # 连接 aritcles 表  para1 是类名 para2是反向引用
    articles = db.relationship('Article',backref='author',lazy='dynamic') 
    # 连接 role 表
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    # 连接 comments 表 
    comments = db.relationship('Comment',backref='commenter')   

    # 用户信息
    real_name = db.Column(db.String(64),nullable=False)
    location = db.Column(db.String(64),nullable=True)
    about_me = db.Column(db.Text(),default="还没有写任何关于我的信息")
    register_date = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    # 是否确认用户注册信息
    confirmed = db.Column(db.Boolean,default=False)
    like_record = db.relationship('Like',backref='liker')
    # 关注的人
    followed = db.relationship('Follow',
                                foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower',lazy='joined'),
                                lazy='dynamic')
    # 关注他的人
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed',lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def vertify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __init__(self,password,location=None,confirmed=False,**kwargs):
        super(User,self).__init__(**kwargs)
        self.password_hash = generate_password_hash(password)
        self.avatar_hash = None
        self.location=location
        self.confirmed=confirmed
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()                 
        # if self.email is not None and self.avatar_hash is None:
        #     self.avatar_hash = gravatar()

    def __repr__(self):
        return '<User %r>' % self.username
   # 10 小时内有效 ,返回token
    def generate_confirmation_token(self,expiration=36000):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dump({'confirm':self.id})

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.load(token)
        except:
            return False
        # 防止恶意用户
        if data.get('confirm') != self.id:
           return False
        self.confirmed = True
        db.session.add(self)

        return True 
    @staticmethod   
    def seed():
        pass   
    # 检查指定权限
    def can(self,permissions):
        return self.role is not None and \
        (self.role.permissions & permissions) == permissions

    def is_adminster(self):
        return self.can(Permission.ADMINSTER)

    # 刷新最后访问时间记录
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    #生成Gravatar URL 表示头像地址
    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

# 关注以及取消关注
    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed=user)
            db.session.add(f)
    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    def is_following(self,user):
        return self.followed.filter_by(followed_id = user.id).first() is not None
    def is_followed_by(self,user):
        return self.follower.filter_by(follower_id=user.id).first() is not None
    @property
    def followed_articles(self):
        return Article.query.join(Follow,Follow.followed_id == Article.author_id).filter_by(Follow.follower_id == self.id)
        
    # 随机生成数据
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                    username=forgery_py.internet.user_name(True),
                    password=forgery_py.lorem_ipsum.word(),
                    confirmed=True,
                    real_name=forgery_py.name.full_name(),
                    location=forgery_py.address.city(),
                    about_me=forgery_py.lorem_ipsum.sentence()
                    )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback() 
  


# 匿名用户类，提供匿名用户的权限     
class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administor(self):
        return False
    # def __init__(self):
        # AnonymousUserMixin.__init__()
        # self.is_authenticated = False
# 设置未登录的用户
login_manager.anonymous_user=AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# 权限常量 存放在一个类里面，清晰
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINSTER = 0x80




# 角色表，表示角色的权限
class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    # 角色是否为默认角色，正常注册会生成一个默认角色 User 其它都是 False
    default = db.Column(db.Boolean,default=False,index=True)
    # 权限整数，表示位标志。给个操作对应一个位位置。
    # 0b0000001(0x01)       关注其它用户
    # 0b0000010(0x02)       发表对其它用户文章的评论
    # 0b0000100(0x04)       写原创文章
    # 0b0001000(0x08)       查处他人发表的不当评论
    # 0b1000000(0x80)       管理网站
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref='role',lazy='dynamic')
    @staticmethod
    def insert_roles():
        roles={
            'User':(Permission.FOLLOW | 
                    Permission.COMMENT |
                    Permission.WRITE_ARTICLES, True),
            'Moderator':(Permission.FOLLOW |
                        Permission.COMMENT | 
                        Permission.WRITE_ARTICLES | 
                        Permission.MODERATE_COMMENTS,False),
            'Adminster':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()


# 文章类 含有字段： id,标题,文章内容，发布日期，文章内容html排版格式，赞数量，阅读量
#         外键： 评论id, 作者id
class Article(db.Model):
    __tablename__='articles'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255),unique=True)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    post_content = db.Column(db.Text)
    post_date = db.Column(db.DateTime,default=datetime.utcnow)
    content_html = db.Column(db.Text)
    comments = db.relationship('Comment',backref='com_article',lazy='dynamic') 
    like = db.Column(db.Integer,default=0)
    # 阅读量
    reads = db.Column(db.Integer,default=0)
    like_record = db.relationship('Like',backref='article',lazy='dynamic')
    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py
        seed()
        user_count=User.query.count()
        for i in range(count):
            u=User.query.offset(randint(1,user_count-1)).first()
            p=Article(post_content=forgery_py.lorem_ipsum.sentences(randint(1,20)),
                    post_date=forgery_py.date.date(True),
                    author=u,
                    title=forgery_py.forgery.lorem_ipsum.title(),
                    like=randint(0,100),
                    reads=randint(0,100))
            db.session.add(p)
            db.session.commit()
   
    # 处理Markdown 文本
    @staticmethod
    def on_changed_content(target,value,oldvalue,initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code','em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p','img']
        attrs = {
        '*': ['class'],
        'a': ['href', 'rel'],
        'img': ['src', 'alt']
        }
        target.content_html = bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),
                tags=allowed_tags,attributes=attrs,strip=True))
# 监听自动转化为html文本的方法 ,处理markdown 的时候打开
db.event.listen(Article.post_content,'set',Article.on_changed_content)




# 评论表格 字段有： 评论内容，评论内容的html排版，评论日期
#       外键： 评论者id, 文章id
class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer, primary_key=True)
    com_content = db.Column(db.Text)
    com_content_html = db.Column(db.Text)
    article_id = db.Column(db.Integer,db.ForeignKey('articles.id'))
    com_date = db.Column(db.DateTime,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    # 评论禁止
    disabled = db.Column(db.Boolean,default=False)
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
       allowed_tags = ['a','abbr','acronym','code','em','i','strong']
       target.com_content_html = bleach.linkify(bleach.clean(
           markdown(value,output_format='html'),
           tags=allowed_tags,strip=True))
        
    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py
        seed()
        article_count = Article.query.count()
        user_count = User.query.count()
        for i in range(count):
            article=Article.query.offset(randint(1,article_count-1)).first()
            user = User.query.offset(randint(1,user_count-1)).first()
            c = Comment(com_content=forgery_py.lorem_ipsum.sentences(randint(1,4)),
                com_date = forgery_py.date.date(True),
                commenter = user,
                com_article=article)
            db.session.add(c)
            db.session.commit()
db.event.listen(Comment.com_content,'set',Comment.on_changed_body)



# 赞表格，字段： 作者id,文章id,是否赞
class Like(db.Model):
    __tablename__='likes'
    id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer,db.ForeignKey('articles.id'))
    is_like = db.Column(db.Boolean,default=False)


