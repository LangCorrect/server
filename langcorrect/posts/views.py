from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from langcorrect.posts.helpers import get_post_counts_by_language
from langcorrect.posts.models import Post, PostVisibility


class PostListView(ListView):
    model = Post
    slug_field = "slug"
    slug_url_kwarg = "slug"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()

        current_user = self.request.user

        if current_user.is_anonymous:
            return qs.filter(permission=PostVisibility.PUBLIC, is_corrected=1)

        native_languages = current_user.native_languages
        studying_languages = current_user.studying_languages

        mode = self.request.GET.get("mode", "teach")
        lang_code = self.request.GET.get("lang_code", None)

        if mode == "following":
            following_users = current_user.following_users
            qs = qs.filter(user__in=following_users)
        elif mode == "learn":
            studying_languages = current_user.studying_languages
            qs = qs.filter(language__in=studying_languages)
        else:
            native_languages = current_user.native_languages
            qs = qs.filter(language__in=native_languages)

        if lang_code:
            if not lang_code == "all":
                qs = qs.filter(language__code=lang_code)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        # page_heading = None
        language_filter_choices = None

        mode = self.request.GET.get("mode", "teach")
        print(self.request.GET)
        selected_lang_code = self.request.GET.get("lang_code", None)

        if mode == "following":
            # page_heading = _("Journals from users you are following")
            pass
        elif mode == "learn":
            # page_heading = _("Journals in the languages you’re studying...")
            language_filter_choices = get_post_counts_by_language(current_user.studying_languages, corrected=True)
        else:
            if current_user.is_authenticated:
                #  page_heading = _("Journals awaiting your correction...")
                language_filter_choices = get_post_counts_by_language(current_user.native_languages)
            else:
                # page_heading = _("Recently corrected journals...")
                pass

        # context["page_heading"] = page_heading
        context["mode"] = mode
        context["language_filters"] = language_filter_choices
        context["selected_lang_code"] = selected_lang_code

        if current_user.is_authenticated:
            context["following_feed"] = Post.available_objects.filter(user__in=current_user.following_users)[:5]

        return context


post_list_view = PostListView.as_view()
