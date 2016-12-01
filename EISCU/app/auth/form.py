# 所有的表单类
from flask_wtf import Form
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,EqualTo,Email,Regexp,Length
# 登录表单
class LoginForm(Form):
    username = StringField(label="用户名",validators=[DataRequired()])
    password = PasswordField(label="密码",validators=[DataRequired()])
    remember_me = BooleanField("记住我")
    submit = SubmitField(label="提交")
    


# 注册表单  
class RegisterForm(Form):
    username = StringField(label="用户名",validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,"用户名必须有字母、数字、下划线或者.组成")])

    password = PasswordField(label="密码",validators=[DataRequired(),EqualTo('password_2',message="两次输入密码必须一致")
])
    password_2 = PasswordField(label="确认密码",validators=[DataRequired()])
    email = StringField(label="邮箱地址",validators=[DataRequired(),Length(1,64),Email()])
    real_name=StringField(label="真实姓名",validators=[DataRequired(),Length(1,64)])
    location = StringField(label="地址")
    submit = SubmitField(label="马上注册")

 