from django.views.generic import ListView

from langcorrect.posts.models import Post


class PostListView(ListView):
    model = Post
    slug_field = "slug"
    slug_url_kwarg = "slug"
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_user = self.request.user
        if current_user.is_authenticated:
            context["following_feed"] = Post.available_objects.filter(user__in=current_user.following_users)[:5]

        return context


post_list_view = PostListView.as_view()
