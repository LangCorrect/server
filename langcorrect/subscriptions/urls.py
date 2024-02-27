from django.urls import path
from django.views.generic import TemplateView

from langcorrect.subscriptions.views import create_checkout_session
from langcorrect.subscriptions.views import manage_premium
from langcorrect.subscriptions.views import stripe_webhook

app_name = "subscriptions"

urlpatterns = [
    path("manage-subscription/", manage_premium, name="manage-subscription"),
    path(
        "create-checkout-session/",
        create_checkout_session,
        name="create-checkout-session",
    ),
    path(
        "success/",
        TemplateView.as_view(template_name="pages/checkout_success.html"),
        name="checkout-success",
    ),
    path(
        "cancel/",
        TemplateView.as_view(template_name="pages/checkout_canceled.html"),
        name="checkout-canceled",
    ),
    path("webhook/", stripe_webhook),
]
