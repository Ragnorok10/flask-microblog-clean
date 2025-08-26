#This page will handle the API user authentication via Tokens

#IMPORTS
import sqlalchemy as sa
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app import db
from app.models import User
from app.api.errors import error_response

#HTTPBasicAuth instance
basic_auth = HTTPBasicAuth()
#HTTPTokenAuth Instance
token_auth = HTTPTokenAuth()


#BASIC AUTH'S
    #veriify_password function
@basic_auth.verify_password
def verify_password(username, password):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user and user.check_password(password):
        return user
    
    #error handler function
@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

#TOKEN AUTH'S
    #verify_token function
@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None

    #token auth error function
@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)