from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from langcorrect.contributions.helpers import update_user_writing_streak
from langcorrect.corrections.helpers import get_post_user_corrections
from langcorrect.corrections.helpers import get_top_correctors
from langcorrect.languages.models import LanguageLevel
from langcorrect.posts.forms import CustomPostForm
from langcorrect.posts.helpers import check_can_create_post
from langcorrect.posts.helpers import get_post_counts_by_language
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostImage
from langcorrect.posts.models import PostVisibility
from langcorrect.prompts.models import Prompt
from langcorrect.utils.storages import get_storage_backend


class PostListView(ListView):
    model = Post
    slug_field = "slug"
    slug_url_kwarg = "slug"
    paginate_by = 25

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and self.get_mode() in [
            "following",
            "learn",
        ]:
            url = reverse("account_login")
            params = urlencode({"next": request.get_full_path()})
            return redirect(f"{url}?{params}")
        return super().dispatch(request, *args, **kwargs)

    def get_mode(self):
        return self.request.GET.get("mode", "teach")

    def get_lang_code(self):
        return self.request.GET.get("lang_code", None)

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related(
                "user",
                "user__contribution",
                "user__stripecustomer",
                "language",
                "prompt",
            )
            .prefetch_related(
                "postimage_set",
                "tags",
            )
        )

        current_user = self.request.user

        if current_user.is_anonymous:
            return qs.filter(permission=PostVisibility.PUBLIC, is_corrected=True)

        mode = self.get_mode()
        lang_code = self.get_lang_code()

        if mode == "following":
            qs = qs.filter(user__in=current_user.get_following_users_ids)
        elif mode == "learn":
            qs = qs.filter(
                language__in=current_user.studying_languages,
                is_corrected=True,
            ).exclude(user=current_user)
        else:
            qs = qs.filter(language__in=current_user.native_languages)

        if lang_code and lang_code != "all":
            qs = qs.filter(language__code=lang_code).order_by(
                "is_corrected",
                "-created",
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        mode = self.get_mode()
        selected_lang_code = self.get_lang_code()

        language_filter_choices = None

        if mode == "learn":
            language_filter_choices = get_post_counts_by_language(
                current_user.studying_languages,
                corrected=True,
            )
        elif mode == "teach" and current_user.is_authenticated:
            language_filter_choices = get_post_counts_by_language(
                current_user.native_languages,
            )

        context.update(
            {
                "mode": mode,
                "language_filters": language_filter_choices,
                "selected_lang_code": selected_lang_code,
            },
        )

        context["popular_correctors"] = {
            "today": get_top_correctors(period="daily"),
            "this_week": get_top_correctors(period="weekly"),
            "this_month": get_top_correctors(period="monthly"),
            "all_time": get_top_correctors(period="all_time"),
        }

        if current_user.is_authenticated:
            following_users_ids = current_user.get_following_users_ids
            context["following_feed"] = Post.available_objects.filter(
                user__in=following_users_ids,
            )[:5]

        return context


post_list_view = PostListView.as_view()


class PostDetailView(DetailView):
    model = Post
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if self.request.user.is_anonymous and obj.permission != PostVisibility.PUBLIC:
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        this_post = self.get_object()
        context["user_corrections"] = get_post_user_corrections(this_post)
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
        if self.request.user.is_authenticated and not check_can_create_post(
            self.request.user,
        ):
            return redirect(reverse("posts:restricted"))
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

        language_level = LanguageLevel.objects.get(
            user=current_user,
            language=form.instance.language,
        )
        form.instance.language_level = language_level.level

        self.object = form.save()
        image_obj = self.request.FILES.get("image", None)
        if image_obj and current_user.is_premium_user:
            storage_backend = get_storage_backend()
            file_key = storage_backend.save(image_obj)
            PostImage.available_objects.create(
                user=current_user,
                post=self.object,
                file_key=file_key,
            )

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
        return super().get_queryset().filter(user=self.request.user)


user_posts_view = UserSubmittedPosts.as_view()


class PostRestrictedView(LoginRequiredMixin, TemplateView):
    template_name = "posts/post_restricted.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_ratio"] = self.request.user.correction_ratio
        context["user_total_sentences"] = self.request.user.postrow_set.count()
        context[
            "user_total_corrections_made"
        ] = self.request.user.corrections_made_count
        context["min_correction_ratio"] = settings.MINIMUM_CORRECTION_RATIO
        return context
