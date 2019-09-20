import os

#
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    DEBUG = False
    TESTING =False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_URL='APP_URL'



class ProductConfig(Config):
	DEBUG = True

class StagingConfig(Config):
	DEVELOPMENT = True
	DEBUG =True

class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True

class TestingConfig(Config):
	TESTING=True


class OriginSystemConfig(object):
    TOKEN = os.environ.get('TM_TOKEN')



class GoogleConfig(object):
    GOOGLE_BOOK='GOOGLE_BOOK'
    GOOGLE_LIST='GOOGLE_LIST'



