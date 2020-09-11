import os

from src.chat.modules import chat_blueprint
from src.microservices import FlaskChassis

microservice = FlaskChassis(service_name="chats", config_file="flask-dev.cfg")
app, db = microservice.app, microservice.db
app.register_blueprint(chat_blueprint, url_prefix='/api/v1/chats')
