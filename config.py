# this will hold our app configuration variables

#imports
import os
from dotenv import load_dotenv

#.ENV creation
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

#create configs - we are going to store them in a class so that way we can have more than 1
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    #scl alchemy configration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    #e-mail error configurations
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['email@ex.com']
    LANGUAGES = ['en', 'es']
    MS_Translator_Key = os.environ.get('MS_TRANSLATOR_KEY')
    POSTS_PER_PAGE = 25
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'