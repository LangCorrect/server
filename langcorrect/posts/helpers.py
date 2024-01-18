from django.conf import settings
from django.db.models import Count, Q
from django.db.models.query import QuerySet

from langcorrect.languages.models import Language, LevelChoices
from langcorrect.posts.models import Post


def get_post_counts_by_language(languages, corrected=False):
    data = {}

    for language in languages:
        count = Post.available_objects.filter(language=language, is_corrected=corrected).count()
        data[language] = count

    return data


def get_post_counts_by_author_native_language(
    native_languages: QuerySet[Language], selected_lang_code: str | None = None, corrected: bool = False
) -> dict[Language, int]:
    """
    Returns a dictionary containing the count of posts based on the post author's native language.

    :param native_languages: A QuerySet of Language objects representing authors' native languages
    :param selected_lang_code: Optional. If provided, filters posts based on the language code.
    :param corrected: Optional. If True, considers only corrected posts; otherwise, includes all posts.
    :return: A dictionary where keys are Language objects and values are the corresponding post counts.
    """
    data = {}

    if selected_lang_code is not None and selected_lang_code != "all":
        selected_lang_code_filter = Q(language__code=selected_lang_code)
    else:
        selected_lang_code_filter = Q()

    qs = (
        Post.available_objects.filter(
            selected_lang_code_filter,
            is_corrected=corrected,
            user__languagelevel__level=LevelChoices.NATIVE,
            user__languagelevel__language__in=native_languages,
        )
        .values("user__languagelevel__language")
        .annotate(count=Count("id"))
    )

    # Build Language to count dictionary from language_id to count
    language_id_to_count = {item["user__languagelevel__language"]: item["count"] for item in qs}
    for language in native_languages:
        data[language] = language_id_to_count.get(language.id, 0)

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
