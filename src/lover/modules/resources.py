from http import HTTPStatus

from flask_restful import Resource, Api

from src.lover.modules import lover_blueprint

lover_restfull = Api(lover_blueprint)


class LoversChatResource(Resource):

    def get(self):
        return {
                   "results": "teste"
               } \
            , HTTPStatus.OK


lover_restfull.add_resource(LoversChatResource, '/teste')