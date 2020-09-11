from http import HTTPStatus
from unittest import TestCase, mock

import pytest
from flask import url_for

from src.microservices import FlaskChassis
from src.user.modules import user_blueprint
from tests.profile.helpers import mocked_get_user, mocked_get_user_without_profile, mocked_get_by_uid_not_exits


class TestUser(TestCase):

    def setUp(self):
        microservice = FlaskChassis(service_name="users", config_file="flask-test.cfg")
        app, db = microservice.app, microservice.db
        app.register_blueprint(user_blueprint, url_prefix='/api/v1/users')
        self.app = app
        self.app.config["SERVER_NAME"] = "localhost.localdomain"
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    @pytest.fixture(autouse=True)
    def mock_verify_token(self):
        patch = mock.patch('firebase_admin.auth.verify_id_token')
        with patch as mock_verify:
            yield mock_verify

    @pytest.fixture(autouse=True)
    def mock_token(self):
        patch = mock.patch('firebase_admin.auth.get_user')
        with patch as mock_verify:
            yield mock_verify

    @mock.patch('src.task.models.user.UserService.get', side_effect=mocked_get_user)
    def test_api_get_by_identifier_if_exits_should_return_profile_correctly(self, mock_get):
        response = self.client.get(url_for("user.userresource"),
                                   query_string={'identifier': 'dedeco@gmail.com'},
                                   headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(mock_get.called)

    @mock.patch('src.task.models.user.UserService.get_by_uid', side_effect=mocked_get_by_uid_not_exits)
    @mock.patch('src.task.models.user.UserService.create', side_effect=mocked_get_user_without_profile)
    def test_api_post_created_user_correctly_should_return_OK(self, mocked_get, mocked_create):
        response = self.client.post(url_for("user.userresource"),
                                    headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(mocked_get.called)
        self.assertTrue(mocked_create.called)
