#This as well as generate the content on a html page, passed through the routes app

#THIS IS AUTH RELATED FORMS

# imports
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo 

#imports for Registration form 
import sqlalchemy as sa
from app import db
from app.models import User

#Babel Language Imports
from flask_babel import _, lazy_gettext as _l

#LOGIN FORM CLASS
#this will capture userinput (login sfuff) with a remember me button
#Create web login form class - this class will hold all user info
class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = StringField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


# Registration form class - will be for seperate html page # will use something similar in own program
class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))
        

# RESET PASSWORD REQUEST CLASS - this will take user e-mail and send a reset password link
class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

# RESET PASSWORD CLASS - this is the form that will load once the user clicks on the link in the URL
class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')]) #this line is to "confirm" the password
    submit = SubmitField(_('Request Password Reset'))