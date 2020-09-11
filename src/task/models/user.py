import datetime

from firebase_admin import auth
from matchbox import models, queries
from matchbox import models as fsm

from src.task.models.profile import Profile


class UserDuplicatedError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'UserDuplicatedError, {0} '.format(self.message)
        else:
            return 'UserDuplicatedError has been raised'


class SuffixFsm(fsm.Model):
    created_at = fsm.TimeStampField()
    last_login_at = fsm.TimeStampField(blank=True)

    class Meta:
        abstract = True


class User(SuffixFsm):
    uid = models.TextField()
    identifier = models.TextField()
    provider = models.TextField()

    profile = models.ReferenceField(Profile)

    def __unicode__(self):
        return self.id

    class Meta:
        collection_name = "users"


class UserFirebaseService:
    def __init__(self, **kwargs):
        if kwargs.get('uid'):
            self._user = auth.get_user(kwargs.get('uid'))
        elif kwargs.get('user_firebase'):
            self._user = kwargs.get('user_firebase')

    def confirm_email_verification_link(self):
        return auth.generate_email_verification_link(self._user.email)

    def generate_password_reset_link(self):
        return auth.generate_password_reset_link(self._user.email)

    def update_email(self, **kwargs):
        self._user = auth.update_user(
            kwargs.get('uid'),
            email=kwargs.get('email'),
            email_verified=False)
        return self._user

    def update_name(self, **kwargs):
        self._user = auth.update_user(
            kwargs.get('uid'),
            display_name=kwargs.get('display_name')
        )
        return self._user

    @property
    def user_firebase(self):
        return self._user


class UserService:

    def __init__(self, **kwargs):
        if kwargs.get('uid'):
            user = auth.get_user(kwargs.get('uid'))
            self._user = User(uid=user.uid,
                              identifier=user.provider_data[0].email,
                              provider=user.provider_data[0].provider_id,
                              created_at=datetime.datetime.fromtimestamp(
                                  user.user_metadata.creation_timestamp / 1e3),
                              last_login_at=datetime.datetime.fromtimestamp(
                                  user.user_metadata.creation_timestamp / 1e3)
                              )
        elif kwargs.get('user'):
            self._user = kwargs.get('user')

    def exists_user_document(self):
        try:
            persisted_user = User.objects.get(uid=self._user.uid)
            if persisted_user:
                self._user = persisted_user
                return True
        except queries.error.DocumentDoesNotExists:
            pass
        return False

    def get_profile_by_user_uid(self, uid):
        self._user = User.objects.get(uid=uid)
        return self._user.profile

    def get_profile(self, args):
        self._user = User.objects.get(**args)
        return self._user.profile

    def get_by_uid(self, uid):
        self._user = User.objects.get(uid=uid)
        return self._user

    def get(self, args):
        self._user = User.objects.get(**args)
        return self._user

    def save(self):
        self._user.save()
        return self._user

    def create(self):
        if not self.exists_user_document():
            self._user.save()
            return self._user
        else:
            raise UserDuplicatedError

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key is not None and value is not None and not key == 'id':
                setattr(self._user, key, value)
        self._user.save()
        return self._user

    def update_profile(self, profile):
        self._user.profile = profile
        self._user.save()

    @staticmethod
    def remove(uid):
        user = User.objects.filter(uid=uid).get()
        profile_id = user.profile.id if user.profile else None
        user.delete()
        return profile_id

    @property
    def user(self):
        return self._user


class UserFeedback(models.Model):
    user_id = models.TextField()
    message = models.TextField()
    created_at = fsm.TimeStampField()

    class Meta:
        collection_name = "users-feedback"


class UserFeedbackService:

    def __init__(self, **kwargs):
        self.user_feedback = UserFeedback(**kwargs)

    def save(self):
        self.user_feedback.save()
        return self.user_feedback


class UserDevice(models.Model):
    user_id = models.TextField()
    device_id = models.TextField()
    os = models.TextField()
    os_version = models.TextField()
    device_model = models.TextField()
    created_at = fsm.TimeStampField()

    class Meta:
        collection_name = "users-device"


class UserDeviceService:

    def __init__(self, **kwargs):
        self._user_device = UserDevice(**kwargs)
        self._user_device.created_at = datetime.datetime.utcnow()

    def save(self):
        self._user_device.save()
        return self._user_device

    def device_has_registered_before(self, user_id, device_id):
        try:
            self._user_device = UserDevice.objects.filter(user_id=user_id, device_id=device_id).get()
        except queries.error.DocumentDoesNotExists:
            return False
        return True

    @property
    def user_device(self):
        return self._user_device
