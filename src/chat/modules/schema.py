from marshmallow import Schema, fields


class ProfilesIdsSchema(Schema):
    profiles = fields.List(fields.Str)
