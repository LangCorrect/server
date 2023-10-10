import logging

from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand

from langcorrect.users.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Verify all email addresses for user accounts that have the flag is_verified set to True"

    def handle(self, *args, **options):
        verified_users = User.objects.filter(is_verified=True).prefetch_related("emailaddress_set")

        for user in verified_users:
            # user may have an email address that has not been stored in allauth's EmailAddress
            if not EmailAddress.objects.filter(email=user.email).exists():
                EmailAddress.objects.create(user=user, email=user.email, verified=True)

            for email_address in user.emailaddress_set.all():
                if not email_address.verified:
                    try:
                        email_address.verified = True
                        email_address.save()
                    except Exception as e:
                        logger.error(f"Failed to verify email {email_address.email}: {e}")
