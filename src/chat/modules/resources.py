from http import HTTPStatus

from flask import request
from flask_restful import Resource, Api, abort
from marshmallow import ValidationError

from src.chat.modules.schema import ProfilesIdsSchema
from src.profile.modules.schema import ProfileResumeSchema
from src.chat.modules import chat_blueprint
from src.task.models.chat import ChatService

chat_restfull = Api(chat_blueprint)


class ChatResource(Resource):

    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
        try:
            data = ProfilesIdsSchema().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        schema = ProfileResumeSchema()

        profiles = ChatService().get_list_profiles(data.get('profiles'))

        return {
                   "message": "Chats profiles",
                   "results": [
                       schema.dump(profiles, many=True)
                   ]
               } \
            , HTTPStatus.OK


chat_restfull.add_resource(ChatResource, '/')
