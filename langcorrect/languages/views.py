from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from langcorrect.languages.forms import LanguageLevelForm
from langcorrect.languages.models import LanguageLevel
from langcorrect.mixins import CanUpdateDeleteObjectMixin


class LanguageLevelListView(LoginRequiredMixin, ListView):
    model = LanguageLevel

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user).order_by("-level")
        return qs


language_level_list_view = LanguageLevelListView.as_view()


class LanguageLevelUpdateView(LoginRequiredMixin, UpdateView):
    model = LanguageLevel
    form_class = LanguageLevelForm

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        return qs

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_success_url(self):
        return reverse("languages:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


language_level_update_view = LanguageLevelUpdateView.as_view()


class LanguageLevelCreateView(LoginRequiredMixin, CreateView):
    model = LanguageLevel
    form_class = LanguageLevelForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_success_url(self):
        return reverse("languages:list")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        return super().form_valid(form)


language_level_create_view = LanguageLevelCreateView.as_view()


class LanguageLevelDeleteView(LoginRequiredMixin, CanUpdateDeleteObjectMixin, DeleteView):
    model = LanguageLevel

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied()

        studying_language_count = request.user.studying_languages.count()

        if studying_language_count == 1:
            raise PermissionDenied("You must have at least one studying language.")

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("languages:list")

    def form_valid(self, form):
        obj = self.get_object()
        obj.delete(soft=False)
        return HttpResponseRedirect(self.get_success_url())


language_level_delete_view = LanguageLevelDeleteView.as_view()
