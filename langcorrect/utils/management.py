# ruff: noqa: FBT002
from django.db import transaction

from langcorrect.corrections.models import Comment
from langcorrect.corrections.models import PostUserCorrection
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostImage
from langcorrect.posts.models import PostRow
from langcorrect.prompts.models import Prompt

NOT_SYSTEM_USER_ERROR = "Target user must be a system user"


class DataManagement:
    @staticmethod
    def migrate_posts(from_user, to_user, require_system_user=True):
        if not from_user and to_user:
            return

        if require_system_user and not to_user.is_system:
            raise ValueError(NOT_SYSTEM_USER_ERROR)

        with transaction.atomic():
            Post.all_objects.filter(user=from_user).update(user=to_user)
            PostRow.all_objects.filter(user=from_user).update(user=to_user)

    @staticmethod
    def delete_post_images(from_user):
        if not from_user:
            return

        with transaction.atomic():
            PostImage.all_objects.filter(user=from_user).delete()

    @staticmethod
    def migrate_prompts(from_user, to_user, require_system_user=True):
        if not from_user and to_user:
            return

        if require_system_user and not to_user.is_system:
            raise ValueError(NOT_SYSTEM_USER_ERROR)

        with transaction.atomic():
            Prompt.all_objects.filter(user=from_user).update(user=to_user)

    @staticmethod
    def migrate_corrections(from_user, to_user, require_system_user=True):
        if not from_user and to_user:
            return

        if require_system_user and not to_user.is_system:
            raise ValueError(NOT_SYSTEM_USER_ERROR)

        with transaction.atomic():
            PostUserCorrection.all_objects.filter(user=from_user).update(user=to_user)

    @staticmethod
    def migrate_comments(from_user, to_user, require_system_user=True):
        if not from_user and to_user:
            return

        if require_system_user and not to_user.is_system:
            raise ValueError(NOT_SYSTEM_USER_ERROR)

        with transaction.atomic():
            Comment.all_objects.filter(user=from_user).update(user=to_user)
