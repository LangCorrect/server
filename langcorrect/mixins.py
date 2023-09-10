from django.core.exceptions import PermissionDenied


class CanUpdateDeleteObjectMixin:
    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if not (obj.user == self.request.user or self.request.user.is_staff):
            raise PermissionDenied()
        return obj
