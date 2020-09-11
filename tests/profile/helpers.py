import json
from datetime import datetime
from http import HTTPStatus
from os.path import abspath, exists
from unittest import mock

import pytest
from matchbox import queries
from flask import make_response, jsonify

from src.task.models.profile import ProfileDuplicatedError
from src.task.models.profile import ProfileService
from src.task.models.user import UserService, User


def get_json_file(file):
    fspath = abspath('tests/resources/' + file)
    if exists(fspath):
        with open(fspath) as f:
            data = json.load(f)
    return data


def mocked_requests_post_profile(*args, **kwargs):
    return make_response(jsonify(
        {
            "message": "Profile created!",
            "results": [
                {
                    "id": "ZdJSIIX5q9NbaK1EqomN"
                }
            ]
        })
        , HTTPStatus.OK)


def mocked_save_profile(*args, **kwargs):
    data = get_json_file("profile-create-request.json")
    profile_service = ProfileService(data)
    profile_service.profile.id = "ZdJSIIX5q9NbaK1EqomN"
    return profile_service.profile


def mocked_get_profile(*args, **kwargs):
    data = get_json_file("profile-response.json").get("results")[0]
    profile_service = ProfileService(data)
    profile_service.profile.id = "KjD4jCqE6sFHb7ioNwgb"
    return profile_service.profile


def mocked_get_user(*args, **kwargs):
    uid = "0yYvOZm9xZbob89ob6l8g0p5IIQ2"
    user_service = UserService(uid=uid)
    user_service.user.id = "MtFXdqrmg9zTb9iG7XcC"
    user = user_service.user
    data = get_json_file("profile-response.json").get("results")[0]
    profile_service = ProfileService(data)
    profile_service.profile.id = "ZdJSIIX5q9NbaK1EqomN"
    user.profile = profile_service.profile
    return user


def mocked_get_user_without_profile(*args, **kwargs):
    uid = "0yYvOZm9xZbob89ob6l8g0p5IIQ2"
    user = User(uid=uid,
                identifier="dedeco@gmail.com",
                provider="password"
                )
    user_profile = UserService(user=user)
    user_profile.user.id = "MtFXdqrmg9zTb9iG7XcC"
    return user_profile.user


def mocked_get_by_uid_not_exits(*args, **kwargs):
    raise queries.error.DocumentDoesNotExists


def mocked_save_profile_duplicated(*args, **kwargs):
    data = get_json_file("profile-create-request.json")
    profile_service = ProfileService(data)
    if profile_service.profile.email == "dedeco@gmail.com":
        raise ProfileDuplicatedError("Email {} already exists, please recovery your account". \
                                     format(profile_service.profile.email))
    if profile_service.pro.exists_mobile_number == "5531996336040":
        raise ProfileDuplicatedError("Mobile number {} already exists, please recovery your account". \
                                     format(profile_service.profile.mobile_number))
    return profile_service.profile


def mocked_update_profile(*args, **kwargs):
    data = get_json_file("profile-create-request.json")
    profile_service = ProfileService(data)
    profile_service.profile.id = "KjD4jCqE6sFHb7ioNwgb"
    if not args[0] == "KjD4jCqE6sFHb7ioNwgb":
        raise queries.error.DocumentDoesNotExists
    return profile_service.profile


def mocked_delete(*args, **kwargs):
    if not args[0] == "KjD4jCqE6sFHb7ioNwgb":
        raise queries.error.DocumentDoesNotExists


@pytest.fixture
def mock_token():
    patch = mock.patch('google.oauth2.id_token.verify_firebase_token')
    with patch as mock_verify:
        yield mock_verify
