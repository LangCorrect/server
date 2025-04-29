from model_utils.managers import SoftDeletableManager


class ActiveUserSoftDeleteManager(SoftDeletableManager):
    def get_queryset(self):
        return super().get_queryset().filter(user__is_active=True)
