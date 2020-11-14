from src.task.models.profile import Profile


class LoverService:

    def __init__(self, profile_id):
        self.id = profile_id

    def get_lovers(self):
        return [p for p in Profile.objects.all() if p.id != self.id]

    def get_lover_by_match_id(self, match_id):
        return Profile.objects.get(id=match_id)
