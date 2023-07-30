from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from langcorrect.prompts.models import Prompt


class PromptListView(LoginRequiredMixin, ListView):
    model = Prompt
    slug_field = "slug"
    slug_url_kwarg = "slug"
    paginate_by = 25

    def get_mode(self):
        return self.request.GET.get("mode", "open")

    def get_lang_code(self):
        return self.request.GET.get("lang_code", None)

    def get_queryset(self):
        current_user = self.request.user

        qs = super().get_queryset().filter(language__in=current_user.all_languages)

        mode = self.get_mode()
        lang_code = self.get_lang_code()

        if mode == "completed":
            qs = qs.filter(post__user=current_user)
        else:
            qs = qs.exclude(post__user=current_user)

        if lang_code and lang_code != "all":
            qs = qs.filter(language__code=lang_code)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        mode = self.get_mode()
        selected_lang_code = self.get_lang_code()

        language_filter_choices = current_user.all_languages

        context.update(
            {
                "mode": mode,
                "language_filters": language_filter_choices,
                "selected_lang_code": selected_lang_code,
            }
        )

        return context


prompt_list_view = PromptListView.as_view()


class PromptDetailView(LoginRequiredMixin, DetailView):
    model = Prompt
    slug_field = "slug"
    slug_url_kwarg = "slug"
    paginate_by = 25


prompt_detail_view = PromptDetailView.as_view()
