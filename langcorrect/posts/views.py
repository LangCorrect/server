from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView

from langcorrect.posts.helpers import get_post_counts_by_language
from langcorrect.posts.models import Post, PostVisibility


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
        return self.request.GET.get("lang_code", None)

    def get_queryset(self):
        qs = super().get_queryset()

        current_user = self.request.user

        if current_user.is_anonymous:
            return qs.filter(permission=PostVisibility.PUBLIC, is_corrected=1)

        mode = self.get_mode()
        lang_code = self.get_lang_code()

        if mode == "following":
            qs = qs.filter(user__in=current_user.following_users)
        elif mode == "learn":
            qs = qs.filter(language__in=current_user.studying_languages)
        else:
            qs = qs.filter(language__in=current_user.native_languages)

        if lang_code and lang_code != "all":
            qs = qs.filter(language__code=lang_code)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        mode = self.get_mode()
        selected_lang_code = self.get_lang_code()

        language_filter_choices = None

        if mode == "learn":
            language_filter_choices = get_post_counts_by_language(current_user.studying_languages, corrected=True)
        elif mode == "teach" and current_user.is_authenticated:
            language_filter_choices = get_post_counts_by_language(current_user.native_languages)

        context.update(
            {
                "mode": mode,
                "language_filters": language_filter_choices,
                "selected_lang_code": selected_lang_code,
            }
        )

        if current_user.is_authenticated:
            context["following_feed"] = Post.available_objects.filter(user__in=current_user.following_users)[:5]

        return context


post_list_view = PostListView.as_view()
