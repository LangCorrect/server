from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from langcorrect.posts.api.views import PostDetailViewSet
from langcorrect.posts.api.views import PostListViewSet
from langcorrect.users.api.views import UserViewSet

router = (
    DefaultRouter(trailing_slash=False)
    if settings.DEBUG
    else SimpleRouter(trailing_slash=False)
)

router.register("users", UserViewSet)
router.register("posts", PostListViewSet, basename="post-list")
router.register("posts", PostDetailViewSet, basename="post-detail")


app_name = "api"
urlpatterns = router.urls
