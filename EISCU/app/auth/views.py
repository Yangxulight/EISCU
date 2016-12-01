from flask import render_template,session,redirect,url_for,request,make_response,flash
from . import auth
from app.auth.form import *
from flask_login import login_user,logout_user,login_required
from app.models import *


#用户登录
@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.vertify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('login.html',title='登录',form=form)


#用户注册
@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,password=form.password.data,real_name=form.real_name.data)
        db.session.add(user)
        db.session.commit()
#        token = user.generate_confirmation_token()
        flash("你现在可以登录了") 
        return redirect(url_for('auth.login'))
    return render_template('register.html',title="注册",form=form)



# 确认邮件功能（没写）          TO BE DONE
@auth.route('/confirm/<token>')
def confirm(token):
    pass


# 用户登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("你已登出")
    # return render_template('logout.html',username=username,title="登出") 
    return redirect(url_for('auth.login')) 


@auth.route('/test')
def test():
    return 'test for auth'



#更新登录用户的访问时间
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirm and \
                request.endpoint[:5] != 'auth':
            return redirect(url_for('auth.unconfirmed'))