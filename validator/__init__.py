from flask import Flask

from flask_mongoengine import MongoEngine
from validator.config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)

db = MongoEngine(app)

from validator.routes import app_routes

app.register_blueprint(app_routes)
