import pytest


from src.microservices import FlaskChassis
from src.profile.modules import profile_blueprint


@pytest.fixture(scope='module')
def app():
    microservice = FlaskChassis(service_name="profiles", config_file="flask-test.cfg")
    app, db = microservice.app, microservice.db
    app.register_blueprint(profile_blueprint, url_prefix='/api/v1/profiles')
    return app


@pytest.fixture(scope='class')
def test_client_logged(request):
    microservice = FlaskChassis(service_name="profiles", config_file="flask-test.cfg")
    flask_app, db = microservice.app, microservice.db
    flask_app.register_blueprint(profile_blueprint, url_prefix='/api/v1/profiles')
    flask_app.config["SERVER_NAME"] = "localhost"
    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    if request.cls is not None:
        request.cls.testing_client = testing_client

    yield testing_client

    ctx.pop()
