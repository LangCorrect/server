from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Verify all email addresses for user accounts that have the flag is_verified set to True"

    def handle(self, *args, **options):
        print("hello")
