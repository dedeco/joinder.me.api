from datetime import date
from random import randrange

from marshmallow import Schema, fields


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def calculate_distance(origin):
    return 10


def get_city(address):
    if address:
        return address.get("administrative_area_level_2", "Not informed")
    else:
        return "Not informed"


def state_or_province(address):
    if address:
        return address.get("administrative_area_level_1", "Not informed")
    else:
        return "Not informed"


class ProfileCardsSchema(Schema):
    id = fields.Str()
    age = fields.Function(lambda obj: calculate_age(obj.birth.get("datetime_birth")))
    sign = fields.Function(lambda obj: obj.sign.get("sun_sign"))
    photo = fields.List(fields.Url())
    name = fields.Str()
    about = fields.Str()
    synastry = fields.Function(lambda x: randrange(100))
    way_of_love = fields.List(fields.Str())
    goals = fields.List(fields.Str())
    interested_in = fields.List(fields.Str())
    looking_for = fields.List(fields.Str())
    state_or_province = fields.Function(lambda obj: state_or_province(obj.address))
    city = fields.Function(lambda obj: get_city(obj.address))
    distance = fields.Function(lambda obj: calculate_distance(obj.location))


