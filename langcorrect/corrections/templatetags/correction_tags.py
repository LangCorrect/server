from django import template

register = template.Library()


@register.inclusion_tag("corrections/partials/user_correction_card.html")
def render_user_correction_card(user, current_user, post, correction_data):
    corrections = correction_data.get("corrections")
    replies = correction_data.get("replies")
    overall_feedback = correction_data.get("overall_feedback")
    return {
        "user": user,
        "current_user": current_user,
        "post": post,
        "corrections": corrections,
        "replies": replies,
        "overall_feedback": overall_feedback,
    }
