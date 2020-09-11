import logging
from datetime import datetime

from flask import current_app as app

from src.task.models.profile import ProfileService
from src.task.models.sing import SignService
from src.task.models.user import UserService, UserFirebaseService, UserFeedbackService, UserDeviceService


def create_profile(data):
    profile_service = ProfileService(**data)
    profile_service.create()
    return {
               "message": "Profile created!",
               "results": [
                   {
                       "id": profile_service.profile.id
                   }
               ]
           }, profile_service.profile


def update_profile_and_user(id, uid, data):
    result, profile = update_profile(id, data)
    if data.get("name"):
        _ = update_user_firebase_name(
            {
                'uid': uid,
                "display_name": profile.name
            }
        )
    if data.get("birth"):
        _ = update_sign_profile(profile)
    return result, profile


def update_email_profile_and_user(id, uid, email):
    profile = ProfileService().get_by_id(id)
    profile = ProfileService(profile=profile).update_email(email)
    _, user = update_user(
        uid,
        {
            "identifier": profile.email
        }
    )
    update_user_firebase_email(
        {
            'uid': user.uid,
            "email": profile.email,
            "email_verified": False
        }
    )
    _, send_user_message_confirm_email(user.uid)
    return {
               "message": "Profile updated!",
               "results": [
                   {
                       "id": profile.id
                   }
               ]
           }, profile


def update_profile(id, data):
    profile = ProfileService().get_by_id(id)
    profile = ProfileService(profile=profile).update(**data)
    return {
               "message": "Profile updated!",
               "results": [
                   {
                       "id": profile.id
                   }
               ]
           }, profile


def update_user(uid, data):
    user = UserService().get_by_uid(uid)
    user = UserService(user=user).update(**data)
    return {
               "message": "User updated!",
               "results": [
                   {
                       "id": user.id
                   }
               ]
           }, user


def update_user_firebase_email(data):
    user_firebase = UserFirebaseService(uid=data.get('uid')).update_email(**data)
    return {
               "message": "User email firebase updated!",
               "results": [
                   {
                       "id": user_firebase.uid
                   }
               ]
           }, user_firebase


def update_user_firebase_name(data):
    user_firebase = UserFirebaseService(uid=data.get('uid')).update_name(**data)
    return {
               "message": "User name firebase updated!",
               "results": [
                   {
                       "id": user_firebase.uid
                   }
               ]
           }, user_firebase


def associate_profile_to_user(user, profile):
    user_service = UserService(user=user)
    user_service.update_profile(profile)
    return {
        "message": "User created and profile had created and associated to user!",
        "results": [
            {
                "user_id": user.id,
                "profile_id": profile.id
            }
        ]
    }


def update_sign_profile(profile):
    sing_service = SignService(profile=profile)
    data = sing_service.find_sun_sign()
    logging.debug("sign api return: ", data)
    profile = ProfileService(profile=profile).update_sing(data)
    return {
        "message": "Sign updated on profile!",
        "results": [
            {
                "profile_id": profile.id
            }
        ]
    }


def delete_profile(reason, uid, id):
    profile = UserService().get_profile_by_user_uid(uid)
    ProfileService(profile=profile).delete(reason, id)
    return {
        "message": "Profile deleted!",
    }


def create_profile_user(user_id, data):
    _, user = create_user(user_id)
    _, profile = create_profile(data)
    result = associate_profile_to_user(user, profile)
    _ = update_sign_profile(profile)
    _ = send_user_message_confirm_email(user.uid)
    return result


def remove_user_and_profile(uid):
    profile_id = UserService().remove(uid)
    if profile_id:
        ProfileService().remove(profile_id)


def create_user(user_uid):
    user_service = UserService(uid=user_uid)
    user_service.create()
    return {
               "message": "User created!",
               "results": [
                   {
                       "id": user_service.user.id
                   }
               ]
           }, user_service.user


def send_user_message_confirm_email(uid):
    user_service = UserFirebaseService(uid=uid)
    from src.user.modules.utils import send_message_confirm_email
    result = send_message_confirm_email(
        user_service.user_firebase.display_name,
        user_service.user_firebase.email,
        user_service.confirm_email_verification_link()
    )
    return result


def update_filter_in_profile(id, data):
    profile = ProfileService().get_by_id(id)
    profile = ProfileService(profile=profile).update_filter(**data)
    return {
               "message": "Profile filter updated!",
               "results": [
                   {
                       "id": profile.id
                   }
               ]
           }, profile


def update_status(id, status):
    profile = ProfileService().get_by_id_all_status(id)
    profile = ProfileService(profile=profile).update_status(status)
    return {
               "message": "Profile reactivated!",
               "results": [
                   {
                       "id": profile.id
                   }
               ]
           }, profile


def save_user_feedback(uid, message):
    user = UserService().get_by_uid(uid)
    user_feedback_service = UserFeedbackService(
        user_id=user.id,
        message=message,
        created_at=datetime.utcnow(),
    )
    user_feedback = user_feedback_service.save()
    return {
        "message": "User feedback saved!",
        "results": [
            {
                "id": user_feedback.id
            }
        ]
    }


def save_user_device(data):
    user_device = None
    user_device_service = UserDeviceService(**data)
    if not user_device_service.device_has_registered_before(data.get("user_id"), data.get("device_id")):
        user_device = user_device_service.save()
    if user_device:
        return True, {
            "message": "User device registered",
            "results": [
                {
                    "id": user_device_service.user_device.id
                }
            ]
        }
    else:
        return False, {
            "message": "User device already registered",
            "results": [
                {
                    "id": user_device_service.user_device.id
                }
            ]
        }


def save_profile_report(id, data):
    profile = ProfileService().get_by_id_all_status(id)
    profile = ProfileService(profile=profile).report_bad_behavior(data, profile.id)
    from src.user.modules.utils import send_message_report_bad_behavior
    result = send_message_report_bad_behavior(
        app.config.get("REPORT_TO_EMAIL"),
        app.config.get("REPORT_TO_NAME"),
        data.get("type_reason"),
        data.get("message")
    )
    return {
        "message": "Profile has been reported",
    }
