#Flask application instance

from flask import Flask
from config import Config

#database imports
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate

#Flask-Login Imports
from flask_login import LoginManager

#Error SMPT handling imports
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

#Flask-Mail imports
from flask_mail import Mail

# Flask Moment imports
from flask_moment import Moment

# Babel Language Imports
from flask import request
from flask_babel import Babel
from flask_babel import lazy_gettext as _l

#ELASTICSEARCH IMPORTS
from elasticsearch import Elasticsearch

#REDIS - Task/Job IMPORTS
from redis import Redis
import rq

#Babel User Request (Must be before app instance)
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

#EXTENSION INSTANCES
    #creating DB instance
db = SQLAlchemy()
migrate = Migrate()
    #initlialize login instance
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page')
    #creating mail instance
mail = Mail()
    #Flask Moment Instance
moment = Moment()
    # Babel Language Instance
babel = Babel()

#CREATE APP FUNCTION

def create_app(config_class=Config):
#This is the Flask application instance
    app = Flask(__name__) 
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    #initiate ELASTICSEARCH attribute in app instance
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None
    
    #initiate REDIS/RQ attribute attribute in app instane
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)

    #ERROR BLUEPRINT import/instance
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    #AUTH BLUEPRINT import/instance
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    #MAIN BLUEPRINT import/instance
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    #CLI BLUEPRINT import/instance
    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)

    #API BLUEPRINT import/instance
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    #Errors SMTP Instance
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')
    
    #return APP
    return app
        
from app import models #here we are importing from the app FOLDER (DIRECTORY), routes = (routes.py) within it

