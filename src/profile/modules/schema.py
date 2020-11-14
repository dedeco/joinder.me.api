import time

from marshmallow import Schema, fields, validate, post_load, validates, ValidationError
import datetime


class CitySchema(Schema):
    city = fields.Str(required=True)


class BirthDetailSchema(Schema):
    place = fields.Nested(CitySchema)
    datetime_birth = fields.DateTime(load_only=False)
    time_birth = fields.Method("get_time_birth")
    date_birth = fields.Method("get_date_birth")

    def get_time_birth(self, obj):
        return obj.get('datetime_birth').strftime("%H:%M")

    def get_date_birth(self, obj):
        return obj.get('datetime_birth').strftime("%d/%m/%Y")


class BirthSchema(Schema):
    place = fields.Nested(CitySchema)
    time_birth = fields.Time(allow_none=True)
    date_birth = fields.Date(required=True)

    @post_load
    def load_time_birth(self, item, **kwargs):
        if not item.get("time_birth"):
            item['time_birth'] = datetime.time()
        return item


class LocationSchema(Schema):
    latitude = fields.Number(required=True)
    longitude = fields.Number(required=True)


from src.content.modules.gender import genders as gender_options
from src.content.modules.goal import goals as goals_options
from src.content.modules.ways_of_love import ways_of_loves as ways_of_love_options
from src.content.modules.interest import interests as interests_options


class RangeSchema(Schema):
    min = fields.Number(required=True)
    max = fields.Number(required=True)


class ProfileFilter(Schema):
    age = fields.Nested(RangeSchema)
    distance = fields.Nested(RangeSchema)


class SingSchema(Schema):
    bot_response = fields.Str()
    sun_sign = fields.Str()


class ProfileSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    photo = fields.List(fields.Url(), allow_none=True)
    about = fields.Str(required=True,
                       validate=validate.Length(max=500))
    email = fields.Email(required=True)
    location = fields.Nested(LocationSchema, required=True)
    genders = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in gender_options.get("genders").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    birth = fields.Nested(BirthSchema, required=True)
    way_of_love = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in ways_of_love_options.get("ways_of_love").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    goals = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in goals_options.get("goals").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    interested_in = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in interests_options.get("interests").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    looking_for = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in gender_options.get("genders").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    configuration = fields.Nested(ProfileFilter)
    status = fields.Str()

    @post_load
    def load_photos(self, item, **kwargs):
        if not item.get("photo"):
            item['photo'] = []
        return item


class ProfileDetailSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    photo = fields.List(fields.Url())
    about = fields.Str(required=True,
                       validate=validate.Length(max=500))
    email = fields.Email(required=True)
    location = fields.Nested(LocationSchema, required=True)
    genders = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in gender_options.get("genders").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    birth = fields.Nested(BirthDetailSchema, required=True)
    way_of_love = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in ways_of_love_options.get("ways_of_love").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    goals = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in goals_options.get("goals").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    interested_in = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in interests_options.get("interests").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    looking_for = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in gender_options.get("genders").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    configuration = fields.Nested(ProfileFilter)
    sign = fields.Nested(SingSchema, required=True)
    status = fields.Str()


class ProfileUpdateSchema(Schema):
    name = fields.Str()
    photo = fields.List(fields.Url())
    about = fields.Str()
    email = fields.Email()
    location = fields.Nested(LocationSchema)
    genders = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in gender_options.get("genders").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    birth = fields.Nested(BirthDetailSchema)
    way_of_love = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in ways_of_love_options.get("ways_of_love").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    goals = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in goals_options.get("goals").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    interested_in = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in interests_options.get("interests").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    looking_for = fields.List(
        fields.Str(required=True,
                   validate=validate.OneOf(
                       [k for d in gender_options.get("genders").get('pt_BR') for k in d.keys()]
                   )
                   )
    )
    configuration = fields.Nested(ProfileFilter)
    status = fields.Str(dump_only=False)


class ProfileUpdateEmailSchema(Schema):
    email = fields.Email()


class ProfileResumeSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str()
    photo = fields.List(fields.Url())


class ProfileReportSchema(Schema):
    type_reason = fields.Str()
    message = fields.Str()


class ProfileOnFridgeSchema(Schema):
    profile_id = fields.Str(required=True)

    @validates("profile_id")
    def validate_profile(self, value):
        if len(value) == 0:
            raise ValidationError("Profile id must not be null.")


class ProfileOnFridgeListSchema(Schema):
    profiles_on_fridge = fields.List(fields.Str())
