# 装饰器，为了启动权限验证功能设置

from functools import wraps
from flask import abort
from flask_login import current_user
from app.models import Permission


# 自定义权限装饰器
def permission_required(permission):
		def decorator(f):
				@wraps(f)
				def decorated_function(*args,**kwargs):
						if not current_user.can(permission):
								abort(403)	# 抛出403异常页面 ，自己编写 
						return f(*args, **kwargs)
				return decorated_function
		return decorator

def admin_required(f):
		return permission_required(Permission.ADMINSTER)(f)