import sys
from http import HTTPStatus

from flask import current_app
from matchbox import models
import requests

from src.profile.modules.schema import BirthDetailSchema


class SignApiError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'SignApiError, {0} '.format(self.message)
        else:
            return 'SignApiError has been raised. Check is sign api is working!'


class SignApiPaymentError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'SignApiPaymentError, {0} '.format(self.message)
        else:
            return 'SignApiPaymentError has been raised. Check is sign api is working!'


class Sign(models.Model):
    sun_sign = models.TextField()


class SignService:

    def __init__(self, **kwargs):
        self._profile = kwargs.get("profile")
        self._birth = BirthDetailSchema().dump(self._profile.birth)

    def find_sun_sign(self):
        PARAMS = {
            "dob": self._birth.get("date_birth"),
            "tob": self._birth.get("time_birth"),
            "lat": self._profile.location.latitude,
            "lon": self._profile.location.longitude,
            "tz": -3,
            "api_key": current_app.config.get("VEDIC_ASTRO_API_KEY")
        }
        try:
            response = requests.get(
                url=self.build_url(),
                params=PARAMS
            )
            if response.json().get("status") == HTTPStatus.PAYMENT_REQUIRED:
                raise SignApiPaymentError("Payment required http error: {0}".format("Vedicastro api key just been "
                                                                                    "expired."))
            return response.json()
        except requests.exceptions.MissingSchema as err:
            raise SignApiError("MissingSchema error: {0}".format(err))

    @staticmethod
    def build_url():
        return "{0}{1}".format(
            current_app.config.get("VEDIC_ASTRO_BASE_URL"),
            "json/horoscope/findsunsign")
