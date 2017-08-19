from flask import Flask


from redis import Redis
from rq import Queue
import rq_dashboard

from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO

from validator.config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)

db = MongoEngine(app)
socketio = SocketIO(app)


redis_conn = Redis()
queue = Queue('high', connection=redis_conn, default_timeout=1800)

from validator.routes import app_routes

app.register_blueprint(app_routes)

# RQ dashboards
app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")