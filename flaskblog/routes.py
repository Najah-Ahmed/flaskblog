from flask import render_template, url_for, flash, redirect,request,abort
import secrets
from PIL import Image
import os
from flaskblog import app ,db,bcrypt
from flaskblog.form import RegistrationForm, LoginForm,UpdateAccountForm , PostForm
from flaskblog.models import User, Post
from flask_login import login_user,current_user,logout_user,login_required


# posts = [
#     {
#         'auther': 'najah said',
#         'title': 'Blog post 1',
#         'content': 'First Post content',
#         'date_posted': 'April 19, 2020'
#     },
#     {
#         'auther': 'najah said',
#         'title': 'Blog post 2',
#         'content': 'Second Post content',
#         'date_posted': 'April 21, 2020'
#     },
#     {
#         'auther': 'najah said',
#         'title': 'Blog post 3',
#         'content': 'Third Post content',
#         'date_posted': 'April 22, 2020'
#     }
# ]


@app.route('/')
@app.route('/home')
def index():
    posts=Post.query.all() 
    return render_template('pages/home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('pages/about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account Has been created . Please Login  ', 'success')
        return redirect(url_for('login'))
    return render_template('pages/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # if form.email.data == 'admin@blog.com' and form.password.data == '12345678':
        #     flash('Login with Success!', 'success')
        #     return redirect(url_for('index'))
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')
            flash('Login with Success!', 'success')
            return redirect(next_page) if next_page else  redirect(url_for('index'))

        else:
            flash(' UnSuccess login! Please Check Email & Password and Try again', 'danger')
    return render_template('pages/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    # form = forgetpasswordForm()
    return redirect(url_for('index'))




def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext =os.path.splitext (form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static/profile_pics',picture_fn)
    
    #image resize 
    output_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)


    i.save(picture_path)
    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required 
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data )
            current_user.image_file=picture_file 
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Update Success!', 'success')
        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file=url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('pages/account.html',image_file=image_file,form=form)


@app.route('/posts/create',methods=['GET','POST'])
@login_required
def add_post():
    form=PostForm()
    if form.validate_on_submit():
        flash('Add Post Success Created !','success')
        post =Post(title=form.title.data,content=form.content.data,auther=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('posts/create.html',title="create Post",form=form)

@app.route('/posts/<post_id>')
def post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('posts/post.html',title=post.title,post=post)

@app.route('/posts/<post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.auther !=  current_user:
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash('Updated Post Success!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method=='GET':
        form.title.data=post.title
        form.content.data=post.content
    return render_template('posts/create.html',title="update Post",form=form,legend="Update Form")

@app.route('/posts/<post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id): 
    post=Post.query.get_or_404(post_id)
    if post.auther !=  current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit( )
    flash('Deleted Post Success!','success')
    return redirect(url_for('index'))
   

@app.route('/forgetpassword') 
def forgetpassword():
    # form = forgetpasswordForm()
    return render_template('pages/forgetpassword.html')
