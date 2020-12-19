import matchbox
from src.task.models.profile import Profile


class ChatService:

    def __init__(self, profile):
        self.profile = profile

    def get_list_profiles(self, ids):
        profiles = []
        for id in [id for id in ids if id not in self.profile.fridge.profiles_on_fridge]:
            try:
                profiles.append(Profile.objects.get(id=id))
            except matchbox.queries.error.DocumentDoesNotExists:
                pass
        return profiles

