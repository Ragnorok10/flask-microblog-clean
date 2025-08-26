#this is an initiation file for our Errors blueprint package

#imports
from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers #in tutorial this is called handlers, but we didn't name it right