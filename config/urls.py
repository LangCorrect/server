import notifications.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

from config.views import index_page_view
from langcorrect.contributions.views import rankings_list_view
from langcorrect.prompts.views import user_prompts_view

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("", view=index_page_view, name="home"),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("langcorrect.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("rankings/", view=rankings_list_view, name="rankings"),
    path("pricing/", TemplateView.as_view(template_name="pages/pricing.html"), name="pricing"),
    path("subscriptions/", include("langcorrect.subscriptions.urls")),
    path("prompts/", include("langcorrect.prompts.urls")),
    path("languages/", include("langcorrect.languages.urls")),
    path("rosetta/", include("rosetta.urls")),
    path("journals/", include("langcorrect.posts.urls")),
    path("inbox/notifications/", include(notifications.urls, namespace="notifications")),
    path("submissions/prompts", user_prompts_view, name="user_prompts"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


api_urlpatterns_v1 = [path("contributions/", include("langcorrect.contributions.urls"))]


# API URLS
urlpatterns += [
    # API base url
    path("api/v1/", include("config.api_router")),
    path("api/v1/", include(api_urlpatterns_v1)),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
