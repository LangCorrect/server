# ruff: noqa: C901, PERF401
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_url(context, kind, param):
    params = []
    current_page = context.request.GET.get("page")
    current_lang = context.request.GET.get("language")
    current_filter = context.request.GET.get("filter")

    def add_param(key, value):
        if value:
            params.append(f"{key}={value}")

    def add_params_except(except_key):
        for key in context.request.GET:
            if key != except_key:
                values = context.request.GET.getlist(key)
                for value in values:
                    params.append(f"{key}={value}")

    if kind == "language":
        add_param("language", param if param != "all" else None)
        add_param("page", current_page)
        add_param("filter", current_filter)
    elif kind == "page":
        add_param("page", param if param != 1 else None)
        add_params_except("page")
    elif kind == "filter":
        add_param("language", current_lang)
        add_param("page", current_page)
        add_param("filter", param)
    elif kind == "mode":
        add_param("mode", param if param != "teach" else None)
        add_params_except("mode")

    return context.request.path + ("?" + "&".join(params) if params else "")
