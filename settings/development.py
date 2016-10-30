"""
Settings using during development process.
"""
try:
    from .base import *
except ImportError:
    print("Cannot import local settings")
    raise

from configparser import RawConfigParser


# Parse configuration file in ini-format.
config = RawConfigParser()
config.read(BASE_DIR.child("config.ini"))

SECRET_KEY = config['misc']['SECRET_KEY']

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "idie",
        'USER': config['database']['USER'],
        'PASSWORD': config['database']['PASSWORD'],
        'HOST': "localhost",
        'PORT': "",
    }
}

THUMBNAIL_DEBUG = True

# Settings from config.ini
THREADS_ON_PAGE = config['board']['THREADS_ON_PAGE']
NEWS_BOARD_ID = config['news']['NEWS_BOARD_ID']
NEWS_ON_PAGE = config['news']['NEWS_ON_PAGE']
