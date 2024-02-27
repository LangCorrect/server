from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from langcorrect.posts.models import Post
from langcorrect.posts.models import PostVisibility


class StaticViewSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return ["home", "community-guidelines", "privacy-policy", "terms-of-service"]

    def location(self, item):
        return reverse(item)


class PostSiteMap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = "https"
    limit = 5000

    def items(self):
        return Post.available_objects.filter(permission=PostVisibility.PUBLIC)

    def lastmod(self, obj):
        return obj.modified
