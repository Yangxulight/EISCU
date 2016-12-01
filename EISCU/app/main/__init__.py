from flask import Blueprint

main = Blueprint("main",__name__)
from app.main import views
from app.models import Permission

# 把Permission 类加入模板上下文,避免render_template多加一个参数
@main.app_context_processor
def inject_permission():
		return dict(Permission=Permission)