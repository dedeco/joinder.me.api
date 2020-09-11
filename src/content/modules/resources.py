from http import HTTPStatus

from flask_cors import cross_origin
from flask_restful import Resource, Api, reqparse

from src.content.modules import states, cache, content_blueprint
from src.content.modules.util import get_parsed_parameters
from . import gender, ways_of_love, goal, looking_for, interest

content_restfull = Api(content_blueprint)


class CitiesStatesResource(Resource):

    @cross_origin()
    def get(self):
        return {
                   "results": states.cities
               } \
            , HTTPStatus.OK


class GenderResource(Resource):

    @cross_origin()
    def get(self):
        return {
                   "results": gender.genders
               } \
            , HTTPStatus.OK


class WayOfLoveResource(Resource):

    @cross_origin()
    def get(self):
        return {
                   "results": ways_of_love.ways_of_loves
               } \
            , HTTPStatus.OK


class GoalsResource(Resource):

    @cross_origin()
    def get(self):
        return {
                   "results": goal.goals
               } \
            , HTTPStatus.OK


class InterestsResource(Resource):

    @cross_origin()
    def get(self):
        return {
                   "results": interest.interests
               } \
            , HTTPStatus.OK


class LookingForResource(Resource):

    @cross_origin()
    def get(self):
        return {
                   "results": looking_for.looking_for
               } \
            , HTTPStatus.OK


import unidecode


class CitiesResource(Resource):

    @cross_origin()
    def get(self):
        args = get_parsed_parameters(reqparse.RequestParser())
        cities = [city for city in [cities for state in states.cities["Brazil"]
                                    for cities in states.cities["Brazil"][state]]
                  if args.get('lookup').upper() in city.upper() or
                  unidecode.unidecode(args.get('lookup')) in unidecode.unidecode(city)]
        return {
                   "results": cities
               } \
            , HTTPStatus.OK


import simplejson


class TermsOfUseResource(Resource):

    @cross_origin()
    def get(self):
        with open('./src/content/modules/templates/pt_BR_terms_of_use.html', 'r') as file:
            data = file.read()
        return {
                   "results": simplejson.dumps(data,  cls=simplejson.encoder.JSONEncoderForHTML)
               } \
            , HTTPStatus.OK


class PrivacyResource(Resource):

    @cross_origin()
    def get(self):
        with open('./src/content/modules/templates/pt_BR_privacy.html', 'r') as file:
            data = file.read()
        return {
                   "results": simplejson.dumps(data, cls=simplejson.encoder.JSONEncoderForHTML)
               } \
            , HTTPStatus.OK


content_restfull.add_resource(CitiesStatesResource, '/states/cities')
content_restfull.add_resource(CitiesResource, '/cities')
content_restfull.add_resource(GenderResource, '/genders')
content_restfull.add_resource(WayOfLoveResource, '/way_of_loves')
content_restfull.add_resource(GoalsResource, '/goals')
content_restfull.add_resource(InterestsResource, '/interests')
content_restfull.add_resource(LookingForResource, '/looking_for')
content_restfull.add_resource(TermsOfUseResource, '/terms_of_use')
content_restfull.add_resource(PrivacyResource, '/privacy')
