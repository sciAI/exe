"""This module includes all things related to app config"""


class Configuration(object):
    """Class with different config variables"""
    DEV = True
    SECRET_KEY = 'Something really secret'
    APP_ROOT = '/opt/sciai/app'
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = set(['csv', 'txt'])

    MONGODB_SETTINGS = [
        {
            'alias': 'main',
            'db': 'jupyter',
            'host': 'localhost',
            'port': 55872
        }
    ]

