from src.task.models.profile import Profile


class ChatService:

    @staticmethod
    def get_list_profiles(ids):
        profiles = []
        for id in ids:
            profiles.append(Profile.objects.get(id=id))
        return profiles
