import copy
import json
from http import HTTPStatus
from unittest import TestCase, mock

import pytest
from flask import url_for

from src.microservices import FlaskChassis
from src.profile.modules import profile_blueprint
from tests.profile.helpers import get_json_file, mocked_save_profile, mocked_save_profile_duplicated, \
    mocked_get_profile, mocked_update_profile, \
    mocked_delete, mocked_get_user, mocked_get_user_without_profile


class TestProfile(TestCase):

    def setUp(self):
        microservice = FlaskChassis(service_name="profiles", config_file="flask-test.cfg")
        app, db = microservice.app, microservice.db
        app.register_blueprint(profile_blueprint, url_prefix='/api/v1/profiles')
        self.app = app
        self.app.config["SERVER_NAME"] = "localhost.localdomain"
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.data = get_json_file("profile-create-request.json")

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

    @mock.patch('src.task.models.user.UserService.create', side_effect=mocked_get_user_without_profile)
    @mock.patch('src.task.models.profile.ProfileService.create', side_effect=mocked_get_profile)
    @mock.patch('src.task.models.user.UserService.update_profile', side_effect=mocked_get_user)
    def test_api_post_created_profile_correctly_should_return_OK(self, mocked_get_user_without_profile,
                                                                 mocked_get_profile, mocked_get_user):
        response = self.client.post(url_for("profile.profileresource"),
                                    data=json.dumps(self.data),
                                    content_type='application/json',
                                    headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.json.get("message"), "User created and profile had created and associated to user!")
        self.assertTrue(mocked_get_user_without_profile.called)
        self.assertTrue(mocked_get_profile.called)
        self.assertTrue(mocked_get_user.called)

    def test_api_post_with_not_required_fields_should_return_UNPROCESSABLE_ENTITY(self):
        data = copy.deepcopy(self.data)
        del data["email"]
        response = self.client.post(url_for("profile.profileresource"),
                                    data=json.dumps(data),
                                    content_type='application/json',
                                    headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(response.json.get("message"),
                         {"email": [
                             "Missing data for required field."
                         ]})

    def test_api_post_with_wrong_types_fields_should_return_UNPROCESSABLE_ENTITY(self):
        data = copy.deepcopy(self.data)
        data["mobile_number"] = "ABCDEF",
        response = self.client.post(url_for("profile.profileresource"),
                                    data=json.dumps(data),
                                    content_type='application/json',
                                    headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(response.json.get("message"),
                         {
                             "mobile_number": [
                                 "Not a valid integer."
                             ]})

    def test_api_post_with_invalid_fields_should_return_UNPROCESSABLE_ENTITY(self):
        data = copy.deepcopy(self.data)
        data["foo"] = "bar",
        response = self.client.post(url_for("profile.profileresource"),
                                    data=json.dumps(data),
                                    content_type='application/json',
                                    headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(response.json.get("message"),
                         {
                             "foo": [
                                 "Unknown field."
                             ]
                         })

    def test_api_post_without_body_should_return_BAD_REQUEST(self):
        response = self.client.post(url_for("profile.profileresource"),
                                    content_type='application/json',
                                    headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json.get("message"),
                         "The browser (or proxy) sent a request that this server could not understand.")

    @mock.patch('src.task.models.user.UserService.create', side_effect=mocked_get_user_without_profile)
    @mock.patch('src.task.models.profile.ProfileService.create', side_effect=mocked_save_profile_duplicated)
    @mock.patch('src.task.models.user.UserService.update_profile', side_effect=mocked_get_user)
    def test_api_post_with_duplicate_email_or_mobile_phone_should_return_CONFLICT(self, mocked_get_user_without_profile
                                                                                     , mock_save
                                                                                     , mocked_get_user):
        for i in range(0, 2):
            response = self.client.post(url_for("profile.profileresource"),
                                        data=json.dumps(self.data),
                                        content_type='application/json',
                                        headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.CONFLICT)
        self.assertEqual(response.json.get("message"), "Profile already exists!")
        self.assertTrue(mock_save.call_count, 2)

    @mock.patch('src.task.models.profile.ProfileService.get', side_effect=mocked_get_profile)
    def test_api_get_by_id_if_exits_should_return_profile_correctly(self, mock_get):
        response = self.client.get(url_for("profile.profileresource"),
                                   query_string={'id': 'KjD4jCqE6sFHb7ioNwgb'},
                                   headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json, get_json_file("profile-response.json"))
        self.assertTrue(mock_get.called)

    @mock.patch('src.task.models.profile.ProfileService.get_by_id', side_effect=mocked_get_profile)
    def test_api_get_by_id_on_path_if_exits_should_return_profile_correctly(self, mock_get):
        response = self.client.get(url_for("profile.profileresource",
                                           id='KjD4jCqE6sFHb7ioNwgb'),
                                   headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json, get_json_file("profile-response.json"))
        self.assertTrue(mock_get.called)

    @mock.patch('src.task.models.profile.ProfileService.update', side_effect=mocked_update_profile)
    def test_api_patch_for_update_if_exits_should_update_profile_correctly(self, mock_update):
        data = get_json_file("profile-update-request.json")
        response = self.client.patch(url_for("profile.profileresource", id="KjD4jCqE6sFHb7ioNwgb"),
                                     data=json.dumps(data),
                                     content_type='application/json',
                                     headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertTrue(mock_update.called)

    @mock.patch('src.task.models.profile.ProfileService.update', side_effect=mocked_update_profile)
    def test_api_patch_for_update_if_not_exits_should_return_NOT_FOUND(self, mock_update_not_found):
        data = get_json_file("profile-update-request.json")
        response = self.client.patch(url_for("profile.profileresource", id="Foo"),
                                     data=json.dumps(data),
                                     content_type='application/json',
                                     headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(mock_update_not_found.called)

    @mock.patch('src.task.models.profile.ProfileService.delete', side_effect=mocked_delete)
    def test_api_delete_if_exists(self, mock_delete):
        response = self.client.delete(url_for("profile.profileresource",
                                              id="KjD4jCqE6sFHb7ioNwgb"),
                                      headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertTrue(mock_delete.called)

    @mock.patch('src.task.models.profile.ProfileService.delete', side_effect=mocked_delete)
    def test_api_delete_if_not_exists_should_return_NOT_FOUND(self, mock_delete):
        response = self.client.delete(url_for("profile.profileresource",
                                              id="Foo"),
                                      headers={'Authorization': 'Bearer 123'})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(mock_delete.called)
