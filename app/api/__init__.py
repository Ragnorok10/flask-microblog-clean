# this will be the initializing page for the API BLUEPRINT we will be creating:

#imports 
from flask import Blueprint

#create blueprint
bp = Blueprint('api', __name__)

from app.api import users, errors, tokens
