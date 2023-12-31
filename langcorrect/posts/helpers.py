"""
NOTE: This file uses local imports within certain functions to resolve circular
dependency issues. If there are suggestions to better handle these dependencies,
further review and refactoring are welcomed.
"""

from django.conf import settings


def get_post_counts_by_language(languages, corrected=False):
    from langcorrect.posts.models import Post  # pylint: disable=import-outside-toplevel

    data = {}

    for language in languages:
        count = Post.available_objects.filter(language=language, is_corrected=corrected).count()
        data[language] = count

    return data


def check_can_create_post(user):
    """
    Checks if the user can create a new post based on their correction ratio.

    The min ratio check is bypassed for premium users or if there are no
    uncorrected journal entries available to correct.
    """

    user_ratio = user.correction_ratio
    has_uncorrected_posts = False

    uncorrected_entries_count = get_post_counts_by_language(user.native_languages)
    for native_language in uncorrected_entries_count.items():
        uncorrected_count = native_language[1]
        if uncorrected_count > 0:
            has_uncorrected_posts = True

    if user.is_premium_user:
        return True
    elif user_ratio == "∞":
        return True
    elif user.correction_ratio > settings.MINIMUM_CORRECTION_RATIO:
        return True
    elif not has_uncorrected_posts:
        return True
    return False


# def hide_old_post_rows_on_edit(post):
#     """
#     Hides all rows associated with a given post when it is edited.
#     """
#     from langcorrect.posts.models import PostRow  # pylint: disable=import-outside-toplevel

#     PostRow.objects.filter(post=post).update(is_actual=False)


# def set_post_row_active(post_row, order):
#     """
#     Sets the specified post row to active and updates its order.
#     """
#     post_row.is_actual = True
#     post_row.order = order
#     post_row.save()
