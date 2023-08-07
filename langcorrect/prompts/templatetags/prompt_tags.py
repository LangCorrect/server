from django import template

register = template.Library()


@register.inclusion_tag("prompts/partials/prompt_card.html")
def render_prompt_card(instance):
    user = instance.user
    created = instance.created
    prompt = instance

    return {
        "user": user,
        "created": created,
        "prompt": prompt,
    }
