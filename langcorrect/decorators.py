from functools import wraps

from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


def premium_required(func):
    """
    Decorator for views that check if a user has premium status, raising a
    PermissionDenied if the condition is not met.
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_premium_user:
            raise PermissionDenied(_("You must be a premium user to access this page."))
        return func(request, *args, **kwargs)

    return wrapper
