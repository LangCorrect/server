import logging

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from langcorrect.subscriptions.helpers import (
    get_current_subscription,
    get_stripe_customer,
    handle_subscription_cancellation,
    serialize_subscription_info,
)
from langcorrect.subscriptions.models import StripeCustomer
from langcorrect.subscriptions.utils import PremiumManager, StripeManager

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


@login_required
def manage_premium(request):
    stripe_customer = get_stripe_customer(request.user)
    subscription = None
    context = {}

    has_active_subscription = stripe_customer and stripe_customer.current_subscription_id

    if request.method == "POST":
        if has_active_subscription:
            # For whatever reason the subscription status returned from this resp
            # uses the key "subscription_status" instead of the normal "status"
            # key. In an effort to save some time and low requests for these
            # pages, we will just fetch the latest subscription instead.
            temp = handle_subscription_cancellation(stripe_customer.current_subscription_id)
            sub_id = temp.get("id")
            subscription = StripeManager.retrieve_subscription(sub_id)
            has_active_subscription = False
    else:
        subscription = get_current_subscription(stripe_customer)

    if subscription:
        context["subscription"] = serialize_subscription_info(subscription)

    if stripe_customer and stripe_customer.premium_until:
        context["premium_until"] = stripe_customer.premium_until
    context["has_active_subscription"] = has_active_subscription
    return render(request, "pages/manage_subscription.html", context)


@login_required
def create_checkout_session(request):
    if request.method == "POST":
        try:
            site_base_url = settings.SITE_BASE_URL

            success_url = site_base_url + reverse_lazy("subscriptions:checkout-success")
            cancel_url = site_base_url + reverse_lazy("subscriptions:checkout-canceled")

            stripe_customer, _ = StripeCustomer.objects.get_or_create(
                user=request.user,
                defaults={"customer_id": StripeManager(customer_email=request.user.email).get_or_create_customer()},
            )

            customer_id = stripe_customer.customer_id

            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                line_items=[
                    {
                        "price": settings.LANGCORRECT_PREMIUM_YEARLY_PRICE_ID,
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                allow_promotion_codes=True,
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except Exception as e:
            logger.error(f"Failed to create a checkout session: {str(e)}")
            return JsonResponse({"error": "An error occurred while creating a checkout session."}, status=400)

        return redirect(checkout_session.url, code=303)


@csrf_exempt
def stripe_webhook(request):
    stripe_webhook_endpoint = settings.STRIPE_WEBHOOK_SECRET_ENDPOINT
    payload = request.body
    sig_header = request.headers["stripe-signature"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, stripe_webhook_endpoint)
    except ValueError as e:
        logger.error(f"Invalid Payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid Signature: {str(e)}")
        return HttpResponse(status=400)

    # Passed signature verification

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Save an order in your database, marked as 'awaiting payment'
        PremiumManager.create_order(session["id"])

        # Check if the order is already paid (for example, from a card payment)
        #
        # A delayed notification payment will have an `unpaid` status, as
        # you're still waiting for funds to be transferred from the customer's
        # account.
        if session.payment_status == "paid":
            PremiumManager.fulfill_order(session)

    elif event["type"] == "checkout.session.async_payment_succeeded":
        session = event["data"]["object"]
        PremiumManager.fulfill_order(session)

    elif event["type"] == "checkout.session.async_payment_failed":
        session = event["data"]["object"]
        PremiumManager.fail_order(session)
        # Send an email to the customer asking them to retry their order
        # email_customer_about_failed_payment(session)

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        PremiumManager.canceled_subscription(subscription)

    return HttpResponse(status=200)
