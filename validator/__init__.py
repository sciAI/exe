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

from flask import Flask

from redis import Redis
from rq import Queue
import rq_dashboard

from flask_mongoengine import MongoEngine
from validator.config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)

db = MongoEngine(app)
redis_conn = Redis()
queue = Queue('high', connection=redis_conn, default_timeout=1800)

from validator.routes import app_routes

app.register_blueprint(app_routes)

# RQ dashboards
app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
