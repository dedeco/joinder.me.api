from random import randrange

from marshmallow import Schema, fields

from datetime import date


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class ProfileCardsSchema(Schema):
    id = fields.Str()
    age = fields.Function(lambda obj: calculate_age(obj.birth.get("datetime_birth")))
    sign = fields.Function(lambda obj: obj.sign.get("sun_sign"))
    photo = fields.List(fields.Url())
    name = fields.Str()
    about = fields.Str()
    synastry = fields.Function(lambda x: randrange(100))