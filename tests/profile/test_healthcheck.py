import unittest
from http import HTTPStatus

import pytest

from flask import url_for


@pytest.mark.usefixtures('client_class')
class TestHealthCheck(unittest.TestCase):

    def setUp(self):
        self.response = self.client.get(url_for('health_check.status'))

    def test_response_ok(self):
        self.assertEqual(HTTPStatus.OK, self.response.status_code)

    def test_api_health_check(self):
        self.assertEqual(self.response.json['status'], 'profiles api microservice running')