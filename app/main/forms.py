#This as well as generate the content on a html page, passed through the routes app

#NON-AUTH related routes (main)

# imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

#imports for Registration form 
import sqlalchemy as sa
from app import db
from app.models import User

#Edit Profile Form imports
from wtforms import TextAreaField
from wtforms.validators import length

#Babel Language Imports
from flask_babel import _, lazy_gettext as _l

#Search form imports
from flask import request
        
# EDIT PROFILE FORM CLASS - will be used to generate content on edit_profile.html
class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[DataRequired()])
    submit=SubmitField(_l('Submit'))

    # Custom constructor and validator for the EditProfileForm
    def __init__(self, original_username, *args, **kwargs):
        # Call the parent class constructor to initialize the form
        super().__init__(*args, **kwargs)
        # Store the user's current username so we can compare it later
        self.original_username = original_username

    # Custom validation method for the username field
    def validate_username(self, username):
        # Only run this check if the username was changed in the form
        if username.data != self.original_username:
            # Query the database to see if the new username is already taken
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            # If a user with that username already exists, raise a validation error
            if user is not None:
                raise ValidationError(_('Please use a different username'))
            
#EMPTYFORM CLASS - will be used to handle follow/unfollow and will only have a CSRF tokenin it

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

# SUBMISSION CLASS - The home page needs to have a form in which users can type new posts.
class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=
                         [DataRequired(), length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

# SEARCHFORM CLASS - will be used to generate the search form
class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)

# PRIVATE MESSAGE CLASS (FORM) - will be used to geneerate the private message form
class MessageForm(FlaskForm):
    message = TextAreaField(_l('Message'), validators=[
        DataRequired(), length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))
