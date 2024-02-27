import logging

from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand

from langcorrect.users.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Store and verify email addresses previously verified in the old code base"

    def handle(self, *args, **options):
        verified_users = User.objects.filter(is_verified=True)

        for user in verified_users:
            # get: if user has attempted to log in after the migration
            #   -> the email has been automatically added to EmailAddress
            # create: if user has NOT attempted to log in
            #   -> the email has not been added to EmailAddress
            previously_verified_email, _ = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
            )

            # verify and set this email as primary if not already manually done by user
            if not (
                previously_verified_email.verified and previously_verified_email.primary
            ):
                try:
                    previously_verified_email.verified = True
                    previously_verified_email.primary = True
                    previously_verified_email.save()
                except Exception:
                    logger.exception("Failed to verify email")
