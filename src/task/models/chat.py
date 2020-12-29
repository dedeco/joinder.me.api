import matchbox
from src.task.models.profile import Profile


class ChatService:

    def __init__(self, profile):
        self.profile = profile

    def get_list_profiles(self, ids):
        profiles = []
        if self.profile.fridge:
            for i in self.profile.fridge.profiles_on_fridge:
                if i in ids:
                    ids.remove(i)
        for id in ids:
            try:
                profiles.append(Profile.objects.get(id=id))
            except matchbox.queries.error.DocumentDoesNotExists:
                pass
        return profiles

