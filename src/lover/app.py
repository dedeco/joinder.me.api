import os

from src.lover.modules import lover_blueprint
from src.microservices import FlaskChassis

microservice = FlaskChassis(service_name="lovers", config_file="flask-dev.cfg")
app, db = microservice.app, microservice.db
app.register_blueprint(lover_blueprint, url_prefix='/api/v1/lovers')
