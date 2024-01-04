from django.conf import settings

from langcorrect.posts.models import Post


def get_post_counts_by_language(languages, corrected=False):
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
