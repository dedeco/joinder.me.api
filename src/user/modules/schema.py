from marshmallow import Schema, fields

from src.profile.modules.schema import ProfileDetailSchema


class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    provider = fields.Str(required=True)
    identifier = fields.Str(required=True)
    created_at = fields.DateTime(required=True)
    profile = fields.Nested(ProfileDetailSchema, required=True)
    last_login_at = fields.DateTime(required=True)
    uid = fields.Str(dump_only=True)


class UserDeviceSchema(Schema):
    id = fields.Str(dump_only=True)
    user_id = fields.Str(required=True)
    device_id = fields.Str(required=True)
    os = fields.Str(required=True)
    os_version = fields.Str(required=True)
    device_model = fields.Str(required=True)
