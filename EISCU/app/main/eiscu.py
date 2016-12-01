# # from flask import Flask
# # app = Flask(__name__)

# # @app.route('/')
# # def index():
# # 		return '<h1>Hello world!</h1>'
# """
# The flask application package.
# """

# from flask import Flask
# from flask_nav import Nav
# from flask_nav.elements import *
# from werkzeug.routing import BaseConverter
# import os
# from flask_bootstrap import Bootstrap
# from flask_login import LoginManager


# # 支持正则表达式
# # @app.route('/user/< regex("[a-z]{3}"): username >') 
# class RegexConverter(BaseConverter):
#     def __init__(self, map,*items):
#         super().__init__(map)
#         self.regex=items[0]

# basedir = os.path.abspath(os.path.dirname(__file__))
# # 注册一个top的nav bar ,可以在jinjia中使用     {% block xxx %} {{ nav.top.render() }} {% endblock %}
# nav = Nav()
# nav.register_element('top',Navbar('EISCU',View('主页','home'),View('关于','about'),View('联系','contact'),View('登录','auth.login')))
# bootstrap=Bootstrap()
# #import EISCU.model
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.sqlite') 
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config.from_pyfile('config.py')
# app.url_map.converters['regex'] = RegexConverter
# nav.init_app(app)
# #    db.init_app(D:\project\python\web_app\EISCU\venvapp)
# #with app.app_context():
# #    # Extensions like Flask-SQLAlchemy now know what the "current" app
# #    # is while within this block. Therefore, you can now run........
# #    db.create_all()
# bootstrap.init_app(app)
# # 注册验证蓝图
# # from auth import auth as auth_blueprint
# from ..auth import auth as auth_blueprint
# app.register_blueprint(auth_blueprint,url_prefix='/auth')

# # 验证管理
# login_manager = LoginManager()
# login_manager.session_protection = 'strong'  #记录客户端 IP 地址和浏览器的用户代理信息，如果发现异动就登出用户。
# login_manager.login_view = 'auth.login'    # 登录路由设定。 用于跳转到登陆页面
# login_manager.init_app(app)

