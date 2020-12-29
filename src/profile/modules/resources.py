from http import HTTPStatus

from firebase_admin.exceptions import InvalidArgumentError
from flask import request, g
from flask_cors import cross_origin
from flask_restful import Resource, abort, reqparse, Api
from marshmallow import ValidationError
from matchbox import queries

from src.microservices.authentication import jwt_required_gcp
from src.task.models.profile import ProfileDuplicatedError, ProfileService, ProfileNotActive, ProfileStatus, \
    ProfileStatusWasNotChanged, ProfileUpdateNotAuthorized
from src.task.models.sing import SignApiError, SignApiPaymentError
from src.task.models.user import UserDuplicatedError, UserService
from src.task.tasks import create_profile_user, delete_profile, update_profile_and_user, \
    update_filter_in_profile, update_email_profile_and_user, update_status, save_profile_report, \
    remove_user_and_profile, save_profile_on_fridge, get_profiles_on_fridge, delete_profile_on_fridge
from . import profile_blueprint
from .schema import ProfileSchema, ProfileUpdateSchema, ProfileFilter, ProfileDetailSchema, ProfileUpdateEmailSchema, \
    ProfileReportSchema, ProfileOnFridgeSchema, ProfileResumeSchema
from .utils import get_parsed_parameters

profile_restfull = Api(profile_blueprint)


class ProfileResource(Resource):

    @cross_origin()
    def get(self, id=None):
        """Search profile_service

        :param: id: str
                email: str

        :return: {"message":"Profile found","results":[{"name":"André de Sousa Araújo","about":"Olá, eu sou a André,
        comigo não tem coré coré, estou aqui para o que der e vier.","way_of_love":"affirming
        words","goals":["dating","friendship","casual dating"],"mobile_number":5531996336040,
        "photo":"http://www.stachastyles.com/wp-content/uploads/2018/02/amazing-freddie-mercury-freddie-mercury
        -hairstyle-20.jpg","id":"KjD4jCqE6sFHb7ioNwgb","genders":["man"],"location":{"longitude":-43.919604,
        "latitude":-19.911073},"looking_for":["transsexual woman","woman"],"email":"dedeco@gmail.com",
        "birth":{"time":"1981-04-27T08:14:00+00:00","place":{"city":"Belo Horizonte"}},"interested_in":["sports",
        "music","books","trips","food"]}]}, HTTPStatus.OK
        """
        try:
            if id:
                profile = ProfileService().get_by_id(id)
            else:
                args = get_parsed_parameters(reqparse.RequestParser(bundle_errors=True))
                args = {k: v for k, v in args.items() if v is not None}
                if args.get("id") or args.get("email"):
                    profile = ProfileService().get(args)
        except queries.error.DocumentDoesNotExists:
            return {
                       "message": "Profile not found"
                   }, HTTPStatus.NOT_FOUND
        except ProfileNotActive:
            return {
                       "message": "Profile not activated or deleted before!"
                   }, HTTPStatus.CONFLICT

        schema = ProfileDetailSchema()

        return {
                   "message": "Profile found",
                   "results": [
                       schema.dump(profile)
                   ]
               } \
            , HTTPStatus.OK

    @cross_origin()
    @jwt_required_gcp
    def post(self):
        """Create a new profile_service

        :param: {"name":"Andre Araujo","email":"dedeco@gmail.com","location":{"latitude":37.3795433,
        "longitude":-122.093595},"birth":{"place":{"city":"Porto de Pedras"},"time":"1996-12-04 23:59:59.999"},
        "photo":["https://firebasestorage.googleapis.com/v0/b/joinder.appspot.com/o/User%2F31c7a170-a0db-11ea-e6eb
        -331439423428?alt=media&token=f61236ee-f8b4-4e21-996c-3ccba0299d40"],"about":"Eu sou sombra e escuridão",
        "genders":["man"],"way_of_love":["affirming_words"],"goals":["dating","friendship"],"interested_in":[
        "series"],"looking_for":["woman"]}

        :return: {"message":"Profile created!","results":[{"id":"ZdJSIIX5q9NbaK1EqomN"}]}
                , HTTPStatus.CREATED
        """
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
        try:
            data = ProfileSchema().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        try:
            result = create_profile_user(g.user_firebase.uid, data)
        except ProfileDuplicatedError:
            return {
                       "message": "Profile already exists!"
                   }, \
                   HTTPStatus.CONFLICT
        except UserDuplicatedError:
            return {
                       "message": "There is a profile associated to this user (token)! So a new profile cannot be "
                                  "created and associate to this profile"
                   }, \
                   HTTPStatus.CONFLICT
        except SignApiError:
            remove_user_and_profile(g.user_firebase.uid)
            return {
                       "message": "The request was well-formed but Api Sing had failed when find the sing by date/time"
                   }, \
                   HTTPStatus.UNPROCESSABLE_ENTITY

        except SignApiPaymentError:
            remove_user_and_profile(g.user_firebase.uid)
            return {
                       "message": "Vedicastro api key just been expired"
                   }, \
                   HTTPStatus.UNPROCESSABLE_ENTITY

        except InvalidArgumentError:
            remove_user_and_profile(g.user_firebase.uid)
            return {
                       "message": "TOO_MANY_ATTEMPTS_TRY_LATER to create a user. Please take a while before try again"
                   }, \
                   HTTPStatus.UNPROCESSABLE_ENTITY

        return result, \
               HTTPStatus.CREATED

    @cross_origin()
    @jwt_required_gcp
    def patch(self, id=None):
        """Update partial/modify profile_service

        :param: {"last_name":"de Sousa Araújo","mobile_number":"123456789"} -> Just some examples of fields

        :return: None, HTTPStatus.NO_CONTENT
        """
        json_data = request.get_json()
        if not json_data or not id:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
        try:
            data = ProfileUpdateSchema().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        try:
            result, profile = update_profile_and_user(id, g.user_firebase.uid, data)
        except queries.error.DocumentDoesNotExists:
            return {"message": "Profile not found!"}, HTTPStatus.NOT_FOUND
        except ProfileDuplicatedError as error:
            return abort(HTTPStatus.BAD_REQUEST, message=error.message)

        if profile:
            return {}, HTTPStatus.NO_CONTENT
        else:
            return {"message": "Profile could not been updated!"}, HTTPStatus.NOT_FOUND

    @cross_origin()
    @jwt_required_gcp
    def put(self, id=None):
        """Update total profile_service

        :param: {"name":"Andre Araujo","email":"dedeco@gmail.com","location":{"latitude":37.3795433,
        "longitude":-122.093595},"birth":{"place":{"city":"Porto de Pedras"},"time":"1996-12-04 23:59:59.999"},
        "photo":["https://firebasestorage.googleapis.com/v0/b/joinder.appspot.com/o/User%2F31c7a170-a0db-11ea-e6eb
        -331439423428?alt=media&token=f61236ee-f8b4-4e21-996c-3ccba0299d40"],"about":"Eu sou sombra e escuridão",
        "genders":["man"],"way_of_love":["affirming_words"],"goals":["dating","friendship"],"interested_in":[
        "series"],"looking_for":["woman"]}

        :return: None, HTTPStatus.NO_CONTENT
        """
        json_data = request.get_json()
        if not json_data or not id:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
        try:
            data = ProfileSchema().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        try:
            result, profile = update_profile_and_user(id, g.user_firebase.uid, data)
        except queries.error.DocumentDoesNotExists:
            return {"message": "Profile not found!"}, HTTPStatus.NOT_FOUND
        except ProfileDuplicatedError as error:
            return abort(HTTPStatus.BAD_REQUEST, message=error.message)

        schema = ProfileDetailSchema()

        if result:
            return {
                       "message": "Profile updated",
                       "results": [
                           schema.dump(profile)
                       ]
                   } \
                , HTTPStatus.OK
        else:
            return {"message": "Profile could not been updated!"}, HTTPStatus.NOT_FOUND

    @cross_origin()
    @jwt_required_gcp
    def delete(self, id=None):
        """Delete profile_service

        :param: None
        :return: None, HTTPStatus.NO_CONTENT
        """
        json_data = request.get_json()
        if not json_data or not id:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST

        reason = json_data.get("reason")
        try:
            result = delete_profile(reason, g.user_firebase.uid, id)
        except queries.error.DocumentDoesNotExists:
            return {"message": "Profile not found!"}, HTTPStatus.NOT_FOUND
        except ProfileNotActive:
            return {"message": "Profile not active anymore! Probably was deleted before"}, HTTPStatus.CONFLICT
        except ProfileUpdateNotAuthorized as error:
            return {"message": error.message}, HTTPStatus.UNAUTHORIZED
        if result:
            return {}, HTTPStatus.NO_CONTENT


class ProfileFilterResource(Resource):

    @cross_origin()
    @jwt_required_gcp
    def post(self, id):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
        try:
            data = ProfileFilter().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        try:
            result, _ = update_filter_in_profile(id, data)
        except queries.error.DocumentDoesNotExists:
            return {"message": "Profile not found!"}, HTTPStatus.NOT_FOUND
        return result, \
               HTTPStatus.OK


class ProfileNewIdentifierResource(Resource):

    @cross_origin()
    @jwt_required_gcp
    def patch(self, id=None):
        """Update email

        :param: {"email":"dedeco@gmail.com"}

        :return: None, HTTPStatus.NO_CONTENT
        """
        json_data = request.get_json()
        if not json_data or not id:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
        try:
            data = ProfileUpdateEmailSchema().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        try:
            result, profile = update_email_profile_and_user(id, g.user_firebase.uid, data.get("email"))
        except queries.error.DocumentDoesNotExists:
            return {"message": "Profile not found!"}, HTTPStatus.NOT_FOUND
        except ProfileDuplicatedError as error:
            return abort(HTTPStatus.BAD_REQUEST, message=error.message)

        if profile:
            return {}, HTTPStatus.NO_CONTENT
        else:
            return {"message": "Profile could not been updated!"}, HTTPStatus.NOT_FOUND


class ProfileReactivateResource(Resource):

    @cross_origin()
    @jwt_required_gcp
    def patch(self, id=None):
        """Reactivate profile

        :return: None, HTTPStatus.NO_CONTENT
        """
        try:
            result, profile = update_status(id, ProfileStatus.ACTIVE.name)
        except queries.error.DocumentDoesNotExists:
            return {"message": "Profile not found!"}, HTTPStatus.NOT_FOUND
        except ProfileDuplicatedError as error:
            return abort(HTTPStatus.BAD_REQUEST, message=error.message)
        except ProfileStatusWasNotChanged as error:
            return abort(HTTPStatus.BAD_REQUEST, message=error.message)

        if profile:
            return {}, HTTPStatus.NO_CONTENT
        else:
            return {"message": "Profile could not been updated!"}, HTTPStatus.NOT_FOUND


class ProfileReportResource(Resource):

    @cross_origin()
    @jwt_required_gcp
    def post(self, id=None):
        json_data = request.get_json()
        if not json_data or not id:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
        try:
            data = ProfileReportSchema().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        try:
            user = UserService().get_by_uid(g.user_firebase.uid)
        except queries.error.DocumentDoesNotExists as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        result = save_profile_report(user, id, data)

        return result \
            , HTTPStatus.OK


class ProfileFridgeResource(Resource):

    @cross_origin()
    @jwt_required_gcp
    def get(self):
        try:
            user = UserService().get_by_uid(g.user_firebase.uid)
        except queries.error.DocumentDoesNotExists:
            return {
                       "message": "There is nobody on Fridge"
                   }, HTTPStatus.NOT_FOUND

        profiles, _ = get_profiles_on_fridge(user)

        schema = ProfileResumeSchema(many=True)

        return {
                   "message": "Profiles on fridge",
                   "results":
                       schema.dump(profiles)
               } \
            , HTTPStatus.OK

    @cross_origin()
    @jwt_required_gcp
    def delete(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
        try:
            data = ProfileOnFridgeSchema().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)

        result = delete_profile_on_fridge(g.user_firebase.uid, data)

        return result \
            , HTTPStatus.NO_CONTENT

    @cross_origin()
    @jwt_required_gcp
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
        try:
            data = ProfileOnFridgeSchema().load(json_data)
        except ValidationError as error:
            return abort(HTTPStatus.UNPROCESSABLE_ENTITY, message=error.messages)
        try:
            result = save_profile_on_fridge(g.user_firebase.uid, data)
        except queries.error.DocumentDoesNotExists:
            return {
                       "message": "There is profiles doesn't exist, so you can not put on fridge"
                   }, HTTPStatus.NOT_FOUND

        return result \
            , HTTPStatus.OK


profile_restfull.add_resource(ProfileResource, "/", '/<id>')
profile_restfull.add_resource(ProfileFilterResource, "/<id>/configuration")
profile_restfull.add_resource(ProfileNewIdentifierResource, '/<id>/new-identifier')
profile_restfull.add_resource(ProfileReactivateResource, '/<id>/reactivate')
profile_restfull.add_resource(ProfileReportResource, '/<id>/report')
profile_restfull.add_resource(ProfileFridgeResource, '/fridge')
