from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired # If someone doesn't enter anything and click the Submit button -> use this to pop up some messages
from wtforms.validators import EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

# Create A Search Form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    
# Create a Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField('Content',validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    # author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")
    

# Create a Form Class 
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color") # We don't care whether the users enter their fav. color, hence, we don't need the validator
    about_author = TextAreaField("About Author")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message="Password Must Match!")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField("Submit")
    

class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    
# Create a Form Class 
class NamerForm(FlaskForm):
    name = StringField("Enter Your Name Here!", validators=[DataRequired()])
    submit = SubmitField("Submit")