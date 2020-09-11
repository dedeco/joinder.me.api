from http import HTTPStatus

from flask import g, request
from flask_cors import cross_origin
from flask_restful import Resource, reqparse, Api, abort
from marshmallow import ValidationError
from matchbox import queries

from src.microservices.authentication import jwt_required_gcp
from src.profile.modules.schema import ProfileSchema, ProfileDetailSchema
from src.task.models.user import UserService, UserFirebaseService
from src.task.tasks import send_user_message_confirm_email, save_user_feedback, save_user_device
from src.user.modules import user_blueprint
from src.user.modules.schema import UserSchema, UserDeviceSchema
from src.user.modules.utils import get_parsed_parameters, send_message_reset_password
from src.task.models.profile import ProfileNotActive, ProfileStatus

user_restfull = Api(user_blueprint)


class UserResource(Resource):

    @jwt_required_gcp
    @cross_origin()
    def get(self):
        try:
            args = get_parsed_parameters(reqparse.RequestParser(bundle_errors=True))
            args = {k: v for k, v in args.items() if v is not None}
            if args.get("identifier") or args.get("uid"):
                user = UserService().get(args)
        except queries.error.DocumentDoesNotExists:
            return {
                       "message": "User not found"
                   }, HTTPStatus.NOT_FOUND

        if not user:
            return {
                       "message": "User not found!"
                   }, HTTPStatus.NOT_FOUND

        schema = UserSchema()

        return {
                   "message": "User found",
                   "results": [
                       schema.dump(user)
                   ]
               } \
            , HTTPStatus.OK


class EmailConfirmResource(Resource):

    @jwt_required_gcp
    @cross_origin()
    def post(self):
        result = send_user_message_confirm_email(g.user_firebase.uid)
        if result.status_code == HTTPStatus.OK:
            return {
                       "message": "Email sent!",
                   } \
                , HTTPStatus.CREATED
        else:
            return {
                       "message": "Email NOT sent!",
                   } \
                , HTTPStatus.BAD_REQUEST


class EmailVerifyResource(Resource):

    @jwt_required_gcp
    @cross_origin()
    def post(self):
        user_service = UserFirebaseService(uid=g.user_firebase.uid)
        if user_service.user_firebase.email_verified:
            return {
                       "message": "Email verified",
                   } \
                , HTTPStatus.OK
        else:
            return {
                       "message": "Email NOT verified yet! Please confirm this email",
                   } \
                , HTTPStatus.NOT_FOUND


class EmailPasswordResetResource(Resource):

    @jwt_required_gcp
    @cross_origin()
    def post(self):
        user_service = UserFirebaseService(uid=g.user_firebase.uid)
        result = send_message_reset_password(user_service.user_firebase.display_name,
                                             user_service.user_firebase.email,
                                             user_service.generate_password_reset_link()
                                             )
        if result.status_code == HTTPStatus.OK:
            return {
                       "message": "Email to reset password was sent!",
                   } \
                , HTTPStatus.CREATED
        else:
            return {
                       "message": "Email to reset password was NOT sent!",
                   } \
                , HTTPStatus.BAD_REQUEST


class UserProfileResource(Resource):

    @jwt_required_gcp
    @cross_origin()
    def get(self, uid=None):
        try:
            if uid:
                user = UserService().get_by_uid(g.user_firebase.uid)
            else:
                args = get_parsed_parameters(reqparse.RequestParser(bundle_errors=True))
                args = {k: v for k, v in args.items() if v is not None}
                if args.get("identifier") or args.get("uid"):
                    user = UserService().get(args)
        except queries.error.DocumentDoesNotExists:
            return {
                       "message": "User not found"
                   }, HTTPStatus.NOT_FOUND

        if not user.profile:
            return {
                       "message": "User without profile!"
                   }, HTTPStatus.NOT_FOUND

        if user.profile.status != ProfileStatus.ACTIVE.name:
            return {
                       "message": "Profile can not be recovery because is not active!"
                   }, HTTPStatus.NOT_FOUND

        schema = ProfileDetailSchema()

        return {
                   "message": "Profile found",
                   "results": [
                       schema.dump(user.profile)
                   ]
               } \
            , HTTPStatus.OK


class UserFeedback(Resource):

    @jwt_required_gcp
    @cross_origin()
    def post(self):

        json_data = request.get_json()
        if not json_data or not id:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST

        message = json_data.get("message")

        try:
            result = save_user_feedback(g.user_firebase.uid, message)
        except queries.error.DocumentDoesNotExists:
            return {"message": "Profile not found!"}, HTTPStatus.NOT_FOUND
        except ProfileNotActive:
            return {"message": "Profile not active anymore! Probably was deleted before"}, HTTPStatus.CONFLICT
        if result:
            return {}, HTTPStatus.NO_CONTENT


class UserDevice(Resource):

    @jwt_required_gcp
    @cross_origin()
    def post(self):

        json_data = request.get_json()
        if not json_data or not id:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST

        try:
            data = UserDeviceSchema().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        registered_before, result = save_user_device(data)

        if not registered_before:
            return result, \
                   HTTPStatus.CONFLICT
        else:
            return result, \
                   HTTPStatus.CREATED


user_restfull.add_resource(UserResource, '/')
user_restfull.add_resource(EmailConfirmResource, '/email/confirm')
user_restfull.add_resource(EmailVerifyResource, '/email/verify')
user_restfull.add_resource(EmailPasswordResetResource, '/email/reset')
user_restfull.add_resource(UserProfileResource, '/<uid>/profile', '/<uid>/profile/')
user_restfull.add_resource(UserFeedback, '/feedback')
user_restfull.add_resource(UserDevice, '/devices')
