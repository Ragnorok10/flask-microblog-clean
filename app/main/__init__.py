# this will serve as the initiation for the MAIN BLUEPRINT

#imports
from flask import Blueprint

#initializer
bp = Blueprint('main', __name__)

#this line imports all the ROUTES from the routes.py module within the MAIN BLUEPRINT
from app.main import routes 