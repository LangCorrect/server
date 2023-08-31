import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

YEARLY_PREMIUM_PRICE_ID = "price_1NkzydBbt6afTexAUGQwOdu4"


def create_checkout_session(request):
    if request.method == "POST":
        try:
            site_base_url = settings.SITE_BASE_URL

            success_url = site_base_url + reverse_lazy("subscriptions:checkout-success")
            cancel_url = site_base_url + reverse_lazy("subscriptions:checkout-canceled")

            stripe.api_key = settings.STRIPE_SECRET_KEY
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price": YEARLY_PREMIUM_PRICE_ID,
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                allow_promotion_codes=True,
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except Exception as e:
            return str(e)

        return redirect(checkout_session.url, code=303)


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_webhook_endpoint = settings.STRIPE_WEBHOOK_SECRET_ENDPOINT
    payload = request.body
    sig_header = request.headers["stripe-signature"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, stripe_webhook_endpoint)
        # print("event type:", event["type"])
    except ValueError as e:  # noqa: 841
        # print(e)
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:  # noqa: 841
        # print(e)
        # Invalid signature
        return HttpResponse(status=400)

    # Passed signature verification

    if event["type"] == "checkout.session.completed":
        session = stripe.checkout.Session.retrieve(event["data"]["object"]["id"], expand=["line_items"])
        line_items = session.line_items  # # noqa: F841

        # breakpoint()

    # Handle the checkout.session.completed event
    if event["type"] == "charge.succeeded":
        print("Payment was successful.")
        # TODO: run some custom code here
        # breakpoint()

    return HttpResponse(status=200)
