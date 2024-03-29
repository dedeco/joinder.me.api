from datetime import datetime
from enum import Enum

from matchbox import models, queries
from matchbox import models as fsm

REPORT = "REPORT"


class ProfileDuplicatedError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ProfileDuplicatedError, {0} '.format(self.message)
        else:
            return 'ProfileDuplicatedError has been raised'


class ProfileNotActive(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ProfileNotActive, {0} '.format(self.message)
        else:
            return 'ProfileNotActive has been raised'


class ProfileStatusWasNotChanged(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ProfileStatusWasNotChanged, {0} '.format(self.message)
        else:
            return 'ProfileStatusWasNotChanged has been raised'


class ProfileUpdateNotAuthorized(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ProfileUpdateNotAuthorized, {0} '.format(self.message)
        else:
            return 'ProfileUpdateNotAuthorized has been raised'


class ProfileConfiguration(models.Model):
    age = models.MapField()
    distance = models.MapField()

    class Meta:
        collection_name = "profiles-configuration"


class ProfileAction(Enum):
    ACCOUNT_DELETED = 1
    ACCOUNT_REACTIVATED = 2
    ACCOUNT_FREEZE = 3
    ACCOUNT_BAD_BEHAVIOR = 4


class ProfileHistory(models.Model):
    reported_by_profile_id = models.TextField()
    target_profile_id = models.TextField()
    action = models.TextField()
    description = models.MapField()
    created_at = fsm.TimeStampField()

    class Meta:
        collection_name = "profiles-history"


class ProfileStatus(Enum):
    ACTIVE = 1
    INACTIVE = 2
    ARCHIVED = 3
    DELETED = 4


class ProfilesOnFridge(models.Model):
    profiles_on_fridge = models.ListField()

    class Meta:
        collection_name = "profiles-on-fridge"

    def __unicode__(self):
        return self.id


class Profile(models.Model):
    name = models.TextField()
    email = models.TextField()
    location = models.GeoPointField()
    photo = models.ListField()
    about = models.TextField()
    genders = models.ListField()
    birth = models.MapField()
    way_of_love = models.ListField()
    goals = models.ListField()
    interested_in = models.ListField()
    looking_for = models.ListField()
    sign = models.MapField(blank=True)
    address = models.MapField(blank=True)

    status = models.TextField()

    configuration = models.ReferenceField(ProfileConfiguration)
    fridge = models.ReferenceField(ProfilesOnFridge)

    class Meta:
        collection_name = "profiles"

    def __unicode__(self):
        return self.id


class ProfileService:

    def __init__(self, **kwargs):
        if kwargs.get('profile'):
            self.profile = kwargs.get('profile')
        elif kwargs:
            self.get_date_birth(kwargs)
            self.profile = Profile(**kwargs)
            self.profile.location = models.GeoPointValue(**kwargs.get("location"))
            self.profile.status = ProfileStatus.ACTIVE.name

    @staticmethod
    def get_date_birth(kwargs):
        if kwargs.get("birth"):
            birth = kwargs.get("birth")
            birth["datetime_birth"] = datetime.combine(
                birth["date_birth"],
                birth["time_birth"]
            )
            del birth["date_birth"]
            del birth["time_birth"]

    def exists_email(self, email=None):
        try:
            profile = Profile.objects.get(email=email or self.profile.email)
            if profile:
                raise ProfileDuplicatedError("Email {} already exists, please recovery your account". \
                                             format(profile.email))
        except queries.error.DocumentDoesNotExists:
            pass
        return False

    def save(self):
        self.profile.save()

    def create(self):
        if self.exists_email():
            raise ProfileDuplicatedError
        else:
            self.profile.save()

    def get(self, args):
        self.profile = Profile.objects.get(**args)
        return self.profile

    @staticmethod
    def profile_exists(profile_id):
        return True if Profile.objects.get(id=profile_id) else False

    def get_by_id(self, id):
        self.profile = Profile.objects.get(id=id)
        if self.profile.status != ProfileStatus.ACTIVE.name:
            raise ProfileNotActive("Profile can not be recovery because is not active!")
        return self.profile

    def get_by_id_all_status(self, id):
        self.profile = Profile.objects.get(id=id)
        return self.profile

    def set(self, data):
        for key, value in data.items():
            if key is not None and value is not None and key not in ['id', 'location', 'profile']:
                setattr(self.profile, key, value)
        if data.get("location"):
            self.profile.location = models.GeoPointValue(**data.get("location"))

    def update(self, **kwargs):
        self.get_date_birth(kwargs)
        for key, value in kwargs.items():
            if key is not None and value is not None and key not in ['id', 'location', 'profile', 'email']:
                setattr(self.profile, key, value)
        self.save()
        return self.profile

    def update_email(self, email):
        if self.profile.email != email and self.exists_email(email=email):
            raise ProfileDuplicatedError
        self.profile.email = email
        self.save()
        return self.profile

    def update_filter(self, **data):
        if self.profile.configuration:
            profile_config = self.profile.configuration
            for key, value in data.items():
                if key is not None and value is not None and key not in ['id']:
                    setattr(profile_config, key, value)
        else:
            profile_config = ProfileConfiguration(**data)
        profile_config.save()
        self.profile.configuration = profile_config
        self.profile.save()
        return self.profile

    def update_sing(self, data):
        self.profile.sign = data.get("response")
        self.profile.save()
        return self.profile

    def update_address(self, address):
        self.profile.address = address
        self.profile.save()
        return self.profile

    def update_status(self, status):
        if self.profile.status == status:
            raise ProfileStatusWasNotChanged("The profile status can not be changed because is already is {0}". \
                                             format(status))
        self.profile.status = status

        profile_history_service = ProfileHistoryService(
            target_profile_id=self.profile.id,
            reported_by_profile_id=self.profile.id,
            action=ProfileAction.ACCOUNT_REACTIVATED.name,
            description={"message": "Login after have deleted."},
            created_at=datetime.utcnow(),
        )
        if status == ProfileStatus.ACTIVE.name:
            profile_history_service.save()

        self.profile.save()
        return self.profile

    def delete(self, reason, id):
        if self.profile.id != id:
            raise ProfileUpdateNotAuthorized("You are trying operation in someone else profile ({0})". \
                                             format(id))
        profile_history_service = ProfileHistoryService(
            target_profile_id=self.profile.id,
            reported_by_profile_id=self.profile.id,
            action=ProfileAction.ACCOUNT_DELETED.name,
            description={"message": reason},
            created_at=datetime.utcnow(),
        )
        profile_history_service.save()

        self.profile.status = ProfileStatus.DELETED.name
        self.profile.save()

    def report_behavior(self, user, data, id):
        if self.profile.id != id:
            raise ProfileUpdateNotAuthorized("You are trying operation in someone else profile ({0})". \
                                             format(id))
        profile_history_service = ProfileHistoryService(
            reported_by_profile_id=user.profile.id,
            target_profile_id=id,
            action=self._set_action(data),
            description=data,
            created_at=datetime.utcnow(),
        )
        profile_history_service.save()

    @staticmethod
    def _set_action(data):
        return ProfileAction.ACCOUNT_BAD_BEHAVIOR.name if data.get("type") == REPORT else ProfileAction.ACCOUNT_FREEZE.name

    @staticmethod
    def remove(id):
        Profile.objects.get(id=id).delete()

    def put_profile_on_fridge(self, profile_id):
        if self.profile_exists(profile_id):
            if self.profile.fridge:
                fridge = self.profile.fridge
                if profile_id not in fridge.profiles_on_fridge:
                    fridge.profiles_on_fridge.append(profile_id)
                    self._save_fridge(fridge)
            else:
                fridge = ProfilesOnFridge()
                profiles = [profile_id, ]
                fridge.profiles_on_fridge = profiles
                self._save_fridge(fridge)
        return self.profile

    def delete_profile_on_fridge(self, profile_id):
        if self.profile.fridge:
            fridge = self.profile.fridge
            if profile_id in fridge.profiles_on_fridge:
                fridge.profiles_on_fridge.remove(profile_id)
                self._save_fridge(fridge)
        return self.profile

    def _save_fridge(self, fridge):
        fridge.save()
        self.profile.fridge = fridge
        self.profile.save()


class ProfileHistoryService:

    def __init__(self, **kwargs):
        if kwargs:
            self.profile_history = ProfileHistory(**kwargs)

    def save(self):
        self.profile_history.save()
        return self.profile_history


import googlemaps

gmaps = googlemaps.Client(key='AIzaSyBAlCaYMw0h6OYJ0CTXWZC11KH-yPlLvTs')


class AddressService:

    def __init__(self, profile):
        self.profile = profile
        self.reverse_geocode_result = gmaps.reverse_geocode(
            (self.profile.location.latitude
             , self.profile.location.longitude))

    def generate_address(self):
        address = {}
        for item in self.reverse_geocode_result[0].get('address_components'):
            address[item.get('types')[0]] = item.get('long_name')
        return address
