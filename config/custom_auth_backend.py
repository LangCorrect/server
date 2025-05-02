import logging

from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth.backends import ModelBackend

from langcorrect.users.helpers import is_system_user

logger = logging.getLogger(__name__)


SYSTEM_USER_LOGIN_ERR_MSG = "System user attempted to authenticate."


class CustomModelBackend(ModelBackend):
    def authenticate(self, request, **credentials):
        user = super().authenticate(request, **credentials)
        if is_system_user(user):
            logger.warning(SYSTEM_USER_LOGIN_ERR_MSG)
            return None
        return user


class CustomAuthenticationBackend(AuthenticationBackend):
    def authenticate(self, request, **credentials):
        user = super().authenticate(request, **credentials)
        if is_system_user(user):
            logger.warning(SYSTEM_USER_LOGIN_ERR_MSG)
            return None
        return user
