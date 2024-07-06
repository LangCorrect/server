from django import template

register = template.Library()


@register.inclusion_tag("corrections/partials/user_correction_card.html")
def render_user_correction_card(user_correction, current_user):
    corrections = user_correction.postcorrection_set.all()
    replies = user_correction.comments.all()

    return {
        "user": user_correction.user,
        "current_user": current_user,
        "user_correction": user_correction,
        "post": user_correction.post,
        "corrections": corrections,
        "replies": replies,
    }


@register.inclusion_tag("corrections/partials/side_by_side_corrections.html")
def render_corrections_side_by_side(post):
    all_post_rows = post.postrow_set.all

    return {"all_post_rows": all_post_rows}


@register.inclusion_tag("corrections/partials/sentence_by_sentence_corrections.html")
def render_corrections_by_sentence(post):
    all_post_rows = post.postrow_set.all

    return {"all_post_rows": all_post_rows}


@register.inclusion_tag("corrections/popular_correctors.html")
def render_popular_correctors(popular_correctors):
    return {"popular_correctors": popular_correctors}
