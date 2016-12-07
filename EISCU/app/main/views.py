"""
Routes and views for the flask application.
"""
from datetime import datetime
from flask import render_template,session,redirect,url_for,request,make_response,flash
from wtforms import Form
from wtforms.validators import Required
from wtforms import StringField,SubmitField,PasswordField
from os import path
from werkzeug.utils import secure_filename
from app.main.form import *
from app.models import *
from app.main import main
from flask_login import login_required
# 使用装饰器
from app.decorators import admin_required,permission_required

# 测试使用权限装饰器，只能管理员访问
@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return "For adminstrators"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderator():
    return "For moderator !"



# 热门文章查看
@main.route('/hot/')
def hot():
    page = request.args.get('page',1,type=int) # 从请求的查询字符串 request.args 获取页数，默认值为1
    pagination = Article.query.order_by(Article.like.desc()).paginate(
        page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out = False)
    posts = pagination.items
    return render_template('hot_article.html',title='热门文章',year=datetime.now().year,posts=posts,pagination=pagination)



# 首页访问，可以发布文章
@main.route('/',methods=['GET','POST'])
@main.route('/index/',methods=['GET','POST'])
# @login_required
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
    # if form.validate_on_submit():
        post = Article(post_content=form.body.data,title=form.title.data,author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        post_id = post.id
        flash("文章发布成功！")
        return redirect(url_for('.post',id=post_id))
    # posts = Article.query.order_by(Article.post_date.desc()).all()
    page = request.args.get('page',1,type=int) # 从请求的查询字符串 request.args 获取页数，默认值为1
    pagination = Article.query.order_by(Article.post_date.desc()).paginate(
        page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out = False)
    posts = pagination.items
    return render_template('index.html',title='发表观点',year=datetime.now().year,form=form,posts=posts,pagination=pagination)

@main.route('/write',methods=['GET','POST'])
@login_required
def write():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Article(post_content=form.body.data,title=form.title.data,author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        post_id = post.id
        flash("文章发布成功！")
        return redirect(url_for('.post',id=post_id))
    return render_template('write.html',title="发表观点",form=form)

@main.route('/upload',methods =['GET','POST'])
@login_required
def upload():
    if request.method == 'POST':
        f = reqeust.files['file']
        basepath = ""


# 关于网站的信息
@main.route('/about/')
def about():
    """Renders the about page."""
    return render_template('about.html',
        title='本站信息',
        year=datetime.now().year,
        message='本站是属于川大管理，详细联系方式如下.')



# 个人的信息中心
@main.route('/user_info/<username>')
@login_required
def user_info(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('info.html',title="个人中心",year=datetime.now().year,user=user)



# 个人主页 他人访问的页面
@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        about(404)
    # posts = user.articles.order_by(Article.post_date.desc()).all()
    page = request.args.get('page',1,type=int) # 从请求的查询字符串 request.args 获取页数，默认值为1
    pagination = user.articles.order_by(Article.post_date.desc()).paginate(
        page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out = False)
    posts = pagination.items
    return render_template('user.html',title=username+'的个人主页',posts=posts,user=user,pagination=pagination)



# 用户资料编辑
@main.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        real_name,about_me,location,email = form.real_name.data,form.about_me.data,form.location.data,form.email.data
        if real_name is not None:
            current_user.real_name = real_name
        if about_me is not None:
            current_user.about_me = about_me
        if location is not None:
            current_user.location = location
        if email is not None:
            current_user.email = email
        db.session.add(current_user)
        flash("你的信息已经被更新!")
        return redirect(url_for('.user_info',username=current_user.username))
    form.real_name.data = current_user.real_name
    form.about_me.data = current_user.about_me
    form.email.data = current_user.email
    form.location.data = current_user.location
    return render_template('edit_profile.html',form=form)



# 测试专用
@main.route('/test/')
def test():
    form = PostForm()
    return render_template('test.html',title='test page',year=datetime.now().year,message='test for something',form=form)



# # 自己定义的在Jinjia2 中可以使用的函数 第一个参数就是函数名字 ,,不过好像blueprint 里面不能用 
# @app.template_test('current_link')
# def current_link(link):
#     return link is request.url  



# 文章的固定url ，便于分享，同时支持文章评论
@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Article.query.get_or_404(id)
    # 增加阅读量
    if post is not None:
        post.reads += 1
        db.session.add(post)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(com_content = form.body.data,
                com_article = post,
                commenter = current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('你的评论提交成功!')
        return redirect(url_for('.post',id=post.id,page=1))
    page = request.args.get('page',1,type=int)
    if page == -1:
        page= (post.comments.count()-1) / current_app.config['EISCU_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.com_date.asc()).paginate(page,per_page=current_app.config['EISCU_COMMENTS_PER_PAGE'],error_out=False)
    comments = pagination.items
    return render_template('post.html',posts=[post],form=form,
                            comments = comments,pagination=pagination)



# 编辑修改文章
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    # 非博主不能编辑该文章
    if current_user != article.author and not current_user.can(Permission.ADMINSTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        article.post_content = form.body.data
        article.title = form.title.data
        db.session.add(article)
        flash('文章修改成功！')
        return redirect(url_for('.post',id=id))
    form.body.data = article.post_content
    form.title.data = article.title
    return render_template('edit_article.html',title="编辑文章",form=form)



# # 为文章点赞 ,双击取消赞
# @main.route('/like/<int:id>',methods=['GET','POST'])
# def add_like(id):
#     article = Article.query.get_or_404(id)
#     like_record = article.like_record.
#     if like_record is None or like_record.is_like == False:
#         like_record = Like(liker = current_user._get_current_object(),article=article)
#         like_record.is_like = True
#         article.like += 1
#     else:
#         like_record = False
#         aritcle.like -= 1
#     db.session.add(like_record)
#     db.session.add(article)
#     db.session.commit()
#     return redirect(url_for('.post',id=id))

# 简化版的点赞功能，后期修改
@main.route('/like/<int:id>',methods=['GET','POST'])
def add_like(id):
    article = Article.query.get_or_404(id)
    article.like += 1
    db.session.add(article)
    db.session.commit()
    return redirect(url_for('.post',id=id))



# 文章分类 (未写)
@main.route('/manage/<int:id>',methods=['GET','POST'])
def manage_article(id):
    pass


# 审核评论
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.order_by(Comment.com_date.desc()).paginate(
        page,per_page=current_app.config['EISCU_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html',comments=comments,
                        pagination=pagination,page=page)


# 评论管理路由
# 关闭屏蔽
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disable = False
    db.session.add(comment)
    # db.session.commit()
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))

# 开启屏蔽
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disable = True
    db.session.add(comment)
    # db.session.commit()
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))



# 关注模块
@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("不存在的用户!")
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash("你已经关注过他了！")
        return redirect(url_for('.user',username=username))
    current_user.follow(user)
    flash("你现在关注了%s" % username)
    return redirect(url_for('.user',username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    pass

@main.route('/followers/<username>')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("不存在的用户！")
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(
        page,per_page=current_app.config['EISCU_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user':item.follower,'datetime':item.follow_date} for item in pagination.items]  
    return render_template('followers.html',user=user,endpoint=".followers",pagination=pagination,follows=follows)      

@main.route('/followed_by/<username>')
@login_required
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("不存在的用户！")
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(
        page,per_page=current_app.config['EISCU_FOLLOWED_PER_PAGE'],
        error_out=False)
    followed = [{'user':item.followed,'datetime':item.follow_date} for item in pagination.items]
    return render_template('followed.html',user=user,endpoint=".followed",pagination=pagination,followed=followed_by)


# 推荐文章
@main.route('/followed_articles')
@login_required
def followed_articles():
    return render_template('recommend.html')

