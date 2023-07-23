from langcorrect.posts.models import Post


def get_post_counts_by_language(languages, corrected=False):
    data = {}

    for language in languages:
        count = Post.available_objects.filter(language=language, is_corrected=corrected).count()
        data[language] = count

    return data
