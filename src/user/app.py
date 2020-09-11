import os

from src.microservices import FlaskChassis
from src.user.modules import user_blueprint

microservice = FlaskChassis(service_name="users", config_file="flask-dev.cfg")
app, db = microservice.app, microservice.db
app.register_blueprint(user_blueprint, url_prefix='/api/v1/users')

