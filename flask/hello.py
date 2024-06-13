from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Create a Flask Instance
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)
# Add Database
# Old SQLite DB
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
# New MySQL DB
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:roger891016@localhost/our_users'
# Secret Key
app.config['SECRET_KEY'] = "confidential"
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Create Admin Page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 18:
        return render_template('admin.html')
    else:
        flash("Sorry, You cannot access the Admin page. Please contact the Administrator!")
        return redirect(url_for('dashboard'))
 

# Create Search Function
@app.route('/search', methods=["POST"]) # Just Post, cuz we don't want to create a page users can go to
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Query the database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html",
                               form=form,
                               searched = post.searched,
                               posts=posts)


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successfully!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Passsword - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again...")
            
    return render_template('login.html', form=form)

# Create Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required # a decorator: direct user to login page if the user hasn't logged in yet
def logout():
    logout_user()
    flash("You Have Been Logged Out! Thanks For Stopping By...")
    return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required # users should login before accessing the dashboard
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST": # post means filling the form
        name_to_update.name = request.form['name'] # different from validator
        name_to_update.email = request.form['email'] 
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username'] 
        name_to_update.about_author = request.form['about_author'] 
        name_to_update.profile_pic = request.files['profile_pic'] 
        
        # Grab Image Name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        
        # Set UUID
        pic_name = str(uuid.uuid1()) + '_' + pic_filename # uuid: Rand Number
        
        # Save Image
        name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        # Change it to a string to save to db
        name_to_update.profile_pic = pic_name
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html",
                                   form=form, 
                                   name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem... Try Again!")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("dashboard.html",
                                form=form,
                                name_to_update=name_to_update,
                                id = id)

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    
    # Only The Author Of the post have the authentication to delete
    if id == post_to_delete.poster_id: 
        try:
            db.session.delete(post_to_delete)
            db.session.commit() # commit changes after modifying the database
            
            # Return a message
            flash("Blog Post Was Deleted!!")
            # Grab all the posts from the database
            # Posts.query: Cuz our posts model is called Posts -> we query the model
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        
        except:
            # Return an error message
            flash("Whoops! There was a problem deleting post, Try again...")
            # Grab all the posts from the database
            # Posts.query: Cuz our posts model is called Posts -> we query the model
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
    else:
        # Return a message
        flash("You Aren't Authorized To Delete That Post!")
        # Grab all the posts from the database
        # Posts.query: Cuz our posts model is called Posts -> we query the model
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)
        
        
@app.route('/posts')
def posts():
    # Grab all the posts from the database
    # Posts.query: Cuz our posts model is called Posts -> we query the model
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST']) # methods=['GET', 'POST'] -> dealing with forms
@login_required # only when users are Logged in can access this page i.e. we can utilize current_user.id to implement authentication issue
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit(): # fill out the form and click the btn - > validate the submission -> new post!
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")        
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id:
        # Auto-Fill the previous form content
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    
    else:
        flash("You Aren't Authorized To Edit This Post...") 
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)
    
# Add Posts Page
@app.route('/add-post', methods=['GET', 'POST'])
# @login_required # users must log in b4 adding posts
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        # Clear the form
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''
        
        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Blog Post Submitted Successfully!")
        
    # Redirect to the webpage
    return render_template("add_post.html", form=form)

# Json Thing
@app.route('/date')
def get_current_date():
    favorite_fruits = {
        "Kyle": "WaterMelon",
        "Emma": "Peach",
        "Tina": "Mango"
    }
    # return {"Date": date.today()}
    return favorite_fruits
    
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    form = UserForm()
    name = None
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")
        
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
                            form=form,
                            name=name,
                            our_users=our_users)
    except:
        flash("Oops! There was a problem deleting user, try again.")
        return render_template("add_user.html",
                            form=form,
                            name=name,
                            our_users=our_users)
    
# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST": # post means filling the form
        name_to_update.name = request.form['name'] # different from validator
        name_to_update.email = request.form['email'] 
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.about_author = request.form['about_author']
        name_to_update.username = request.form['username'] 
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem... Try Again!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("update.html",
                                form=form,
                                name_to_update=name_to_update,
                                id = id)
    
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    name = None
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password!!!
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, about_author=form.about_author, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.about_author = ''
        form.password_hash.data = ''
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users)

# Create a route decorator
@app.route('/') # Home page of the web

# 127.0.0.1 -> localhost
# def index():
#     return "<h1> Hello World!</h1>"

def index():
    first_name = "Kyle"
    stuff = "This is a <strong>bold</strong> text"
    flash("Welcome To Our Website!") # pop up message
    fruits = ["apple", "banana", "peach", "watermelon", "guava", 41]
    return render_template("index.html", 
                           first_name=first_name,
                           stuff=stuff,
                           fruits=fruits)

# localhost:5000/user/john
@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name=name)

# Create Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Create Password Test Page 
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    
     
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear the form
        form.email.data = ''
        form.password_hash.data = ''
        
        # Lookup User By Email Address
        pw_to_check =  Users.query.filter_by(email=email).first()
        
        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)
    
    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)

# Create Name Page 
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")
    
    return render_template("name.html",
                           name=name,
                           form=form)
    
    
# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text) # text area, paragraph
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    slug = db.Column(db.String(255))
    # Foreign Key To Link Users(refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id')) # u in lowercase: reference the call to database
    
# Create Model: what we want to save into the database
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    profile_pic = db.Column(db.String(1000), nullable=True) # Not saving the picture, but storing its name; hence, we use String
    
    #Users Can Have Many Posts
    posts = db.relationship('Posts', backref='poster') # Reference the Posts class
    
    # Do some password stuff!!
    password_hash = db.Column(db.String(128))
    
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
     
    # Create A String
    def __repr__(self):
        return "<Name %r>" % self.name
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)