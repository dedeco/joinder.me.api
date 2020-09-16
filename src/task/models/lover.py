from src.task.models.profile import Profile


class LoverService:

    def __init__(self, id):
        self.id = id

    def get_lovers(self):
        return [p for p in Profile.objects.all() if p.id != self.id]
