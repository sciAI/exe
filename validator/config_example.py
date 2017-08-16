"""
    App config
"""

class Configuration(object):
    """Class with different config variables"""
    DEV = True
    SECRET_KEY = 'Something really secret'
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = set(['csv', 'txt'])
    PYTHON3_PIP = '../py3env/bin/pip'
    PYTHON2_PIP = '../py2env/bin/pip'
    PYTHON3_PYTHON = '../py3env/bin/python'
    PYTHON2_PYTHON = '../py2env/bin/python'

    MONGODB_SETTINGS = [
        {
            'alias': 'main',
            'db': 'jupyter',
            'host': 'localhost',
            'port': 12345
        }
    ]

