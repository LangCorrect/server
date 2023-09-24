from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from langcorrect.posts.models import Post


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "submissions/post_list.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        return qs


post_list_view = PostListView.as_view()
