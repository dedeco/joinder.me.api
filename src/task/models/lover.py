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
        lovers = []
        for p in Profile.objects.all():
            if p.id != self.profile.id and self.profile.fridge:
                if p.id not in self.profile.fridge.profiles_on_fridge:
                    lovers.append(p)
            else:
                lovers.append(p)

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
