from http import HTTPStatus

from flask import url_for
from flask_restful import Resource, Api, reqparse

from src.microservices.authentication import jwt_required_gcp
from src.lover.modules import lover_blueprint
from src.lover.modules.schema import ProfileCardsSchema
from src.lover.modules.utils import get_paginated_list, get_parameters_url, get_parsed_parameters
from src.task.models.lover import LoverService

lover_restfull = Api(lover_blueprint)


class LoverResource(Resource):

    @jwt_required_gcp
    def get(self):
        args = get_parsed_parameters(reqparse.RequestParser(bundle_errors=True))
        args = {k: v for k, v in args.items() if v is not None}
        if args.get("id"):
            lovers = LoverService(id).get_lovers()
            schema = ProfileCardsSchema(many=True)
            return get_paginated_list(
                schema,
                lovers,
                url_for('lover.loverresource'),
                get_parameters_url(args),
                start=args.get('start'),
                limit=args.get('limit')
            ), HTTPStatus.OK

        else:
            return {
                       "message": "Profiles not found"
                   }, HTTPStatus.NOT_FOUND


lover_restfull.add_resource(LoverResource, '/')
