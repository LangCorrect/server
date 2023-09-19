from django import template

register = template.Library()


@register.inclusion_tag("posts/partials/post_card.html")
def render_post_card(instance, current_user, correctors, disable_stretched_link=False, disable_text_truncation=False):
    user = instance.user
    created = instance.created
    post = instance

    already_corrected = False

    if current_user in correctors:
        already_corrected = True

    return {
        "user": user,
        "created": created,
        "current_user": current_user,
        "already_corrected": already_corrected,
        "post": post,
        "disable_stretched_link": disable_stretched_link,
        "disable_text_truncation": disable_text_truncation,
    }


@register.inclusion_tag("posts/partials/post_reply_card.html")
def render_post_reply_card(instance, current_user):
    user = instance.user
    created = instance.created

    return {"user": user, "current_user": current_user, "created": created, "instance": instance}
