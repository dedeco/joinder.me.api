from src.lover.modules.schema import LoverCardSchema
from src.task.models.profile import Profile
from matchbox import models, queries


class LoversService:

    def __init__(self, profile):
        self.profile = profile
        self.lovers = Lovers(profile=profile, lovers=self.get_calculate_lovers())

    def save_lovers(self):
        self.lovers.save()
        return self.lovers

    def get_calculate_lovers(self):
        schema = LoverCardSchema(many=True)
        lovers = [p for p in Profile.objects.all() \
                  if p.id != self.profile.id \
                  and p.id not in self.profile.fridge.profiles_on_fridge]
        return schema.dump(lovers)

    @staticmethod
    def get_lover_by_match_id(match_id):
        return Profile.objects.get(id=match_id)


class Lovers(models.Model):
    profile = models.ReferenceField(Profile)
    lovers = models.ListField()

    class Meta:
        collection_name = 'lovers'

    def __unicode__(self):
        return self.id


class Lover(models.Model):
    age = models.IntegerField()
    sign = models.TextField()
    photo = models.ListField()
    name = models.TextField()
    about = models.TextField()
    synastry = models.IntegerField()
    way_of_love = models.ListField()
    goals = models.ListField()
    interested_in = models.ListField()
    looking_for = models.ListField()
    state_or_province = models.TextField()
    city = models.TextField()
    distance = models.IntegerField()

    def __unicode__(self):
        return self.id
