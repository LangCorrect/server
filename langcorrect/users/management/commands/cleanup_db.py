from django.core.management.base import BaseCommand
from django.db import transaction

from langcorrect.users.models import User
from langcorrect.utils.management import DataManagement


def has_data(user):
    return (
        user.post_set.exists()
        or user.prompt_set.exists()
        or user.postusercorrection_set.exists()
        or user.comment_set.exists()
    )


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            deleted_users = User.all_objects.filter(
                username__icontains="deleted_",
            ).all()

            system_user = User.objects.get(username="system", is_system=True)

            for user in deleted_users:
                with transaction.atomic():
                    DataManagement.migrate_posts(
                        from_user=user,
                        to_user=system_user,
                    )
                    DataManagement.delete_post_images(from_user=user)
                    DataManagement.migrate_prompts(
                        from_user=user,
                        to_user=system_user,
                    )
                    DataManagement.migrate_corrections(
                        from_user=user,
                        to_user=system_user,
                    )
                    DataManagement.migrate_comments(
                        from_user=user,
                        to_user=system_user,
                    )
                    user.delete()

            users_with_empty_email = User.all_objects.filter(
                email="",
                is_system=False,
            )

            for user in users_with_empty_email:
                with transaction.atomic():
                    if not has_data(user):
                        user.delete()

            User.all_objects.filter(
                is_active=False,
                last_login__isnull=True,
            ).delete()
