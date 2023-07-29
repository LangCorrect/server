from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView


class IndexPageTemplateView(TemplateView):
    template_name = "pages/home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("posts:list"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["disable_page_container"] = True
        return context


index_page_view = IndexPageTemplateView.as_view()
