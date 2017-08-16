"""
    App config
"""

class Configuration(object):
    """Class with different config variables"""
    DEV = True
    SECRET_KEY = 'Something really secret'
    # APP_ROOT = '/opt/sciai/app'
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    UPLOAD_FOLDER = '/opt/jupyter-testing/validator/static/uploads'
    ALLOWED_EXTENSIONS = set(['csv', 'txt'])
    PYTHON3_PIP = '/opt/jupyter-testing/py3env/bin/pip'
    PYTHON2_PIP = '/opt/jupyter-testing/py2env/bin/pip'
    PYTHON3_PYTHON = '/opt/jupyter-testing/py3env/bin/python'
    PYTHON2_PYTHON = '/opt/jupyter-testing/py2env/bin/python'

    MONGODB_SETTINGS = [
        {
            'alias': 'main',
            'db': 'jupyter',
            'host': 'mongo.prod.sci.xp7nz.com' #'localhost',
            #'port': #55872
        }
    ]

