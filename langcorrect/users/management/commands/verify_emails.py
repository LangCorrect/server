from django.core.management.base import BaseCommand

from langcorrect.users.models import User


class Command(BaseCommand):
    help = "Verify all email addresses for user accounts that have the flag is_verified set to True"

    def handle(self, *args, **options):
        verified_users = User.objects.filter(is_verified=True)

        for user in verified_users:
            verified_user_emails = user.emailaddress_set.all()
            try:
                for email in verified_user_emails:
                    email.verified = True
                    email.save()
            except Exception as e:
                print(e)
