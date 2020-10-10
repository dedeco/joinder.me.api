from functools import wraps
from http import HTTPStatus

import firebase_admin
from firebase_admin import auth
from flask import request, g


# Here is a custom decorator that verifies the JWT is present in
# the request
def jwt_required_gcp(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            id_token = request.headers['Authorization'].split(' ').pop()
        except KeyError:
            return {"message": "Unauthorized. Please, inform some valid token"}, \
                   HTTPStatus.UNAUTHORIZED
        except ValueError:
            return {"message": "Invalid token, Unauthorized"}, \
                   HTTPStatus.UNAUTHORIZED
        try:
            decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        except firebase_admin._auth_utils.InvalidIdTokenError:
            return {"message": "Expired token or invalid token, Unauthorized"}, \
                   HTTPStatus.UNAUTHORIZED
        except firebase_admin._auth_utils.UserNotFoundError:
            return {"message": "No user record found for the provided user ID"}, \
                   HTTPStatus.UNAUTHORIZED
        g.user_firebase = auth.get_user(decoded_token['uid'])
        # from pprint import pprint
        # pprint(vars(g.user))
        if not g.user_firebase:
            return {"message": "Invalid token, Unauthorized"}, \
                   HTTPStatus.UNAUTHORIZED
        return fn(*args, **kwargs)

    return wrapper
