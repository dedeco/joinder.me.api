from flask import Blueprint
from src.microservices import FlaskChassis
from flask_caching import Cache
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

microservice = FlaskChassis(service_name="contents", config_file="flask-dev.cfg")
app, db = microservice.app, microservice.db

cache = Cache()
cache.init_app(app, config={'CACHE_TYPE': 'simple',
                            'CACHE_DEFAULT_TIMEOUT': 300
                            })
content_blueprint = Blueprint('content', __name__)



from . import resources



