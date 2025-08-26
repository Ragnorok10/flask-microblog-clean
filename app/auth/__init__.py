# this will serve as the initiation for the AUTH BLUEPRINT

#imports
from flask import Blueprint

#initializer
bp = Blueprint('auth', __name__)

#this line imports all the ROUTES from the routes.py module within the AUTH BLUEPRINT
from app.auth import routes