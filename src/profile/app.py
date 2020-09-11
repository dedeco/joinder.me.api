import os

from src.microservices import FlaskChassis
from src.profile.modules import profile_blueprint

microservice = FlaskChassis(service_name="profiles", config_file="flask-dev.cfg")
app, db = microservice.app, microservice.db
app.register_blueprint(profile_blueprint, url_prefix='/api/v1/profiles')
