from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DetailView, ListView

from langcorrect.languages.models import Language
from langcorrect.prompts.forms import CustomPromptForm
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

    def get_lang_code(self):
        return self.request.GET.get("lang_code", None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prompt_responses = self.get_object().post_set.all()

        response_languages = list(prompt_responses.values_list("language__code", flat=True).distinct().order_by())

        selected_lang_code = self.get_lang_code()
        language_filter_choices = Language.objects.filter(code__in=response_languages)

        if selected_lang_code and selected_lang_code != "all":
            prompt_responses = prompt_responses.filter(language__code=selected_lang_code)

        context.update(
            {
                "language_filters": language_filter_choices,
                "selected_lang_code": selected_lang_code,
                "prompt_responses": prompt_responses,
            }
        )

        return context


prompt_detail_view = PromptDetailView.as_view()


class PromptCreateView(CreateView):
    model = Prompt
    form_class = CustomPromptForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


prompt_create_view = PromptCreateView.as_view()


class UserPromptsView(LoginRequiredMixin, ListView):
    model = Prompt
    template_name = "prompts/user_prompts.html"
    paginate_by = 20

    def get_queryset(self):
        current_user = self.request.user
        qs = super().get_queryset().filter(user=current_user)

        return qs


user_prompts_view = UserPromptsView.as_view()
