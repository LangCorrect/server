from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from langcorrect.contributions.helpers import update_user_writing_streak
from langcorrect.corrections.helpers import get_popular_correctors, populate_user_corrections
from langcorrect.corrections.models import CorrectedRow, OverallFeedback, PerfectRow
from langcorrect.languages.models import LanguageLevel, LevelChoices
from langcorrect.posts.forms import CustomPostForm
from langcorrect.posts.helpers import (
    check_can_create_post,
    get_post_counts_by_author_native_language,
    get_post_counts_by_language,
)
from langcorrect.posts.models import Post, PostImage, PostReply, PostVisibility
from langcorrect.prompts.models import Prompt
from langcorrect.users.models import User
from langcorrect.utils.storages import get_storage_backend


class PostListView(ListView):
    model = Post
    slug_field = "slug"
    slug_url_kwarg = "slug"
    paginate_by = 25

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and self.get_mode() in ["following", "learn"]:
            url = reverse("account_login")
            params = urlencode({"next": request.get_full_path()})
            return redirect(f"{url}?{params}")
        return super().dispatch(request, *args, **kwargs)

    def get_mode(self):
        return self.request.GET.get("mode", "teach")

    def get_lang_code(self):
        return self.request.GET.get("lang_code", "all")

    def get_author_native_lang_code(self):
        return self.request.GET.get("author_native_lang_code", "all")

    def get_queryset(self):
        qs = super().get_queryset()

        current_user = self.request.user

        if current_user.is_anonymous:
            return qs.filter(permission=PostVisibility.PUBLIC, is_corrected=True)

        mode = self.get_mode()
        lang_code = self.get_lang_code()
        author_native_lang_code = self.get_author_native_lang_code()

        if mode == "following":
            qs = qs.filter(user__in=current_user.get_following_users_ids)
        elif mode == "learn":
            qs = qs.filter(language__in=current_user.studying_languages, is_corrected=True).exclude(user=current_user)
        else:
            qs = qs.filter(language__in=current_user.native_languages)

        if lang_code and lang_code != "all":
            qs = qs.filter(language__code=lang_code).order_by("is_corrected", "-created")

        if author_native_lang_code and author_native_lang_code != "all":
            qs = qs.filter(
                user__languagelevel__language__code=author_native_lang_code,
                user__languagelevel__level=LevelChoices.NATIVE,
            ).order_by("is_corrected", "-created")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        mode = self.get_mode()
        selected_lang_code = self.get_lang_code()
        selected_author_native_lang_code = self.get_author_native_lang_code()

        language_filter_choices = None
        author_native_language_filter_choices = None

        if mode == "learn":
            language_filter_choices = get_post_counts_by_language(current_user.studying_languages, corrected=True)
        elif mode == "teach" and current_user.is_authenticated:
            language_filter_choices = get_post_counts_by_language(current_user.native_languages)

        if current_user.is_authenticated:
            author_native_language_filter_choices = get_post_counts_by_author_native_language(
                current_user.studying_languages, selected_lang_code
            )

        context.update(
            {
                "mode": mode,
                "language_filters": language_filter_choices,
                "author_native_language_filters": author_native_language_filter_choices,
                "selected_author_native_lang_code": selected_author_native_lang_code,
                "selected_lang_code": selected_lang_code,
            }
        )

        context["popular_correctors"] = {
            "today": get_popular_correctors(period="today"),
            "this_week": get_popular_correctors(period="this_week"),
            "this_month": get_popular_correctors(period="this_month"),
            "all_time": get_popular_correctors(period="all_time"),
        }

        if current_user.is_authenticated:
            following_users_ids = current_user.get_following_users_ids
            context["following_feed"] = Post.available_objects.filter(user__in=following_users_ids)[:5]

        return context


post_list_view = PostListView.as_view()


class PostDetailView(DetailView):
    model = Post
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if self.request.user.is_anonymous and obj.permission != PostVisibility.PUBLIC:
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        this_post = self.get_object()

        corrector_user_ids = set(
            CorrectedRow.available_objects.filter(post=this_post).values_list("user__id", flat=True)
        )
        corrector_user_ids.update(
            list(PerfectRow.available_objects.filter(post=this_post).values_list("user__id", flat=True))
        )
        corrector_user_ids.update(
            list(OverallFeedback.available_objects.filter(post=this_post).values_list("user__id", flat=True))
        )

        correctors = User.objects.filter(id__in=corrector_user_ids)

        corrected_rows = (
            CorrectedRow.available_objects.filter(user__in=correctors, post=this_post)
            .select_related("post_row", "post", "user")
            .prefetch_related("post_row", "post", "user")
        )

        perfect_rows = (
            PerfectRow.available_objects.filter(user__in=correctors, post=this_post)
            .select_related("post_row", "post", "user")
            .prefetch_related("post_row", "post", "user")
        )

        feedback_rows = OverallFeedback.available_objects.filter(user__in=correctors, post=this_post)

        postreply_rows = PostReply.available_objects.filter(post=this_post)

        context["user_corrections"] = populate_user_corrections(
            perfect_rows, corrected_rows, feedback_rows, postreply_rows
        )
        return context


post_detail_view = PostDetailView.as_view()


class PostUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Post
    form_class = CustomPostForm
    success_message = _("Post successfully updated")

    def get_form_kwargs(self):
        user = self.get_object().user
        kwargs = super().get_form_kwargs()
        kwargs["user"] = user
        return kwargs

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


post_update_view = PostUpdateView.as_view()


class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Post
    form_class = CustomPostForm
    success_message = _("Post successfully added")

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and not check_can_create_post(self.request.user):
            raise PermissionDenied(_("Your correction ratio is too low."))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        prompt_slug = self.kwargs.get("prompt_slug", None)
        if prompt_slug:
            context["prompt"] = get_object_or_404(Prompt, slug=prompt_slug)

        return context

    def form_valid(self, form):
        current_user = self.request.user
        form.instance.user = current_user

        context = self.get_context_data()
        prompt = context.get("prompt", None)
        if prompt:
            form.instance.prompt = prompt

        language_level = LanguageLevel.objects.get(user=current_user, language=form.instance.language)
        form.instance.language_level = language_level.level

        self.object = form.save()
        image_obj = self.request.FILES.get("image", None)
        if image_obj and current_user.is_premium_user:
            storage_backend = get_storage_backend()
            file_key = storage_backend.save(image_obj)
            PostImage.available_objects.create(user=current_user, post=self.object, file_key=file_key)

        update_user_writing_streak(self.object.user)

        return HttpResponseRedirect(self.get_success_url())


post_create_view = PostCreateView.as_view()


class PostDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Post
    success_message = _("Post successfully deleted")
    success_url = reverse_lazy("posts:list")

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(user=self.request.user)

    def form_valid(self, form):
        post = self.get_object()

        if post.postimage_set.exists():
            post_image_obj = post.postimage_set.first()
            file_key = post_image_obj.file_key
            storage_backend = get_storage_backend()
            storage_backend.delete(file_key)
            post_image_obj.delete()

        return super().form_valid(form)


post_delete_view = PostDeleteView.as_view()


class UserSubmittedPosts(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/user_posts.html"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        return qs


user_posts_view = UserSubmittedPosts.as_view()
