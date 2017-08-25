#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##############################################################################
#
#   sci.AI EXE
#   Copyright(C) 2017 sci.AI
#
#   This program is free software: you can redistribute it and / or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY
#   without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see < http://www.gnu.org/licenses/ >.
#
##############################################################################

activate_this = '/opt/exe/py2env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys

sys.path.insert(0, "/opt/exe/")

from validator import app as application
