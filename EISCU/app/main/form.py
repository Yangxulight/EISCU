# 所有的表单类
from flask_wtf import Form
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextField
from wtforms.validators import DataRequired,EqualTo,Email,Regexp,Length
from flask_pagedown.fields import PageDownField

# 编辑资料表单        
class EditProfileForm(Form):
		real_name=StringField(label="真实姓名",validators=[DataRequired(),Length(1,64)])
		about_me = TextField(label="关于我",validators=[DataRequired()])
		location = StringField(label="地址",validators=[DataRequired(),Length(1,64)])
		email = StringField(label="邮箱地址",validators=[DataRequired(),Length(1,64),Email()])
		submit = SubmitField(label="提交修改")
  
# 发布博客表单
class PostForm(Form):
		title = StringField(label='标题',validators=[DataRequired(),Length(1,255)])
		body = PageDownField('思考，从写下你这一刻的想法开始。',validators=[DataRequired()])
		submit = SubmitField(label='发布博客')

class CommentForm(Form):
		body = PageDownField('你的看法',validators=[DataRequired()])
		sumbit = SubmitField('发表')

