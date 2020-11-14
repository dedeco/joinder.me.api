from http import HTTPStatus

from flask import url_for, g
from flask_restful import Resource, Api, reqparse
from matchbox import queries

from src.lover.modules import lover_blueprint
from src.lover.modules.schema import ProfileCardsSchema
from src.lover.modules.utils import get_paginated_list, get_parameters_url, get_parsed_parameters_for_deck, \
    get_parsed_parameters
from src.microservices.authentication import jwt_required_gcp
from src.task.models.lover import LoverService
from src.task.models.user import UserService

lover_restfull = Api(lover_blueprint)


class LoverDeckResource(Resource):

    @jwt_required_gcp
    def get(self):
        args = get_parsed_parameters_for_deck(reqparse.RequestParser(bundle_errors=True))
        args = {k: v for k, v in args.items() if v is not None}
        user = UserService().get_by_uid(g.user_firebase.uid)
        lovers = LoverService(user.profile.id).get_lovers()
        schema = ProfileCardsSchema(many=True)
        return get_paginated_list(
            schema,
            lovers,
            url_for('lover.loverdeckresource'),
            get_parameters_url(args),
            start=args.get('start'),
            limit=args.get('limit')
        ), HTTPStatus.OK


class LoverResource(Resource):

    @jwt_required_gcp
    def get(self):
        args = get_parsed_parameters(reqparse.RequestParser(bundle_errors=True))
        args = {k: v for k, v in args.items() if v is not None}
        user = UserService().get_by_uid(g.user_firebase.uid)
        if args.get("match_id"):
            try:
                lover = LoverService(user.profile.id).get_lover_by_match_id(args.get("match_id"))
            except queries.error.DocumentDoesNotExists:
                return {
                           "message": "Profile match id not found"
                       }, HTTPStatus.NOT_FOUND
            schema = ProfileCardsSchema()
            return {
                "results": schema.dump(lover)
            }
        else:
            return {
                       "message": "Profiles not found"
                   }, HTTPStatus.NOT_FOUND


lover_restfull.add_resource(LoverDeckResource, '/')
lover_restfull.add_resource(LoverResource, '/details/')
