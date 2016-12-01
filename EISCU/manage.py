from werkzeug.utils import secure_filename
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand,upgrade
from app import app,db
from app.models import *
# app.debug=True
manager = Manager(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)


# python manage.py dev
#  在编写程序的时候启动，随着代码的修改自动实时发生页面刷新，减少调试负担
@manager.command
def dev():
    from livereload import Server
    live_server = Server(app.wsgi_app)
    live_server.watch('**/*.*')
    live_server.serve(open_url=False)   

@manager.command
def test():
    pass

# python managy.py deploy
# 部署建立数据库  初次运行会自动建立数据库表格
# 非初次运行的话，如果数据库表格有更新，则自动创建新的表结构
@manager.command
def deploy():
	upgrade()


# python managy.py debug
# 以调试模式运行，出错会在浏览器显示错误信息，仅在开发调试中使用
@manager.command
def debug():
	app.run(debug=True)



# python managy.py run
# 运行发布的app， 不显示调试错误信息，正常发布的时候使用
@manager.command
def run():
	app.run(debug=False)



def make_shell_context():
     return dict(app=app, db=db, User=User, Role=Role,Article=Article)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)



# python manage.py reset_fake_data
# 自动创立数据库，并且填充随机生成的数据，用数据扩充站点的页面内容显示，以达到有一定量用户正常使用时候的效果。
@manager.command
def reset_fake_data():
		db.drop_all()
		db.create_all()
		Role.insert_roles()
		User.generate_fake(100)
		Article.generate_fake(100)
		Comment.generate_fake(100)
		u=User(username='admin',password='password',email='admin@boss.com',real_name='God',confirmed=1,location='SCU',about_me='I am the administer!')
		db.session.add(u)
		db.session.commit()



# @manager.command
# def run():
# 		manager.run()
if __name__=="__main__":
	# dev()				# 实时监控修改的代码
	# run()			# 部署运行
	# app.run(debug=True)
	manager.run()
