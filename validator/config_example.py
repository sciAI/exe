# sci.AI EXE
# Copyright(C) 2017 sci.AI

# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY
# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see < http: // www.gnu.org / licenses / >.

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

