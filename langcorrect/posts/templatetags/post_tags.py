from django import template

register = template.Library()


@register.inclusion_tag("posts/partials/post_card.html")
def render_post_card(instance, current_user, disable_stretched_link=False):
    user = instance.user
    created = instance.created
    post = instance

    return {
        "user": user,
        "created": created,
        "current_user": current_user,
        "post": post,
        "disable_stretched_link": disable_stretched_link,
    }


@register.inclusion_tag("posts/partials/post_reply_card.html")
def render_post_reply_card(instance):
    user = instance.user
    created = instance.created

    return {"user": user, "created": created, "instance": instance}
