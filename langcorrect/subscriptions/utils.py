import logging
from datetime import datetime

import stripe
from django.conf import settings
from django.utils import timezone

from langcorrect.subscriptions.models import PaymentHistory, PaymentStatus, Product, StripeCustomer

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


class StripeManager:
    def __init__(self, customer_id=None, customer_description=None, customer_email=None):
        self.customer_id = customer_id
        self.customer_description = customer_description
        self.customer_email = customer_email

    def get_or_create_customer(self) -> str:
        """
        Get or create a Stripe customer object.

        Stripe API Reference: https://stripe.com/docs/api/customers/object

        Returns:
            str: customer_id
        """
        if self.customer_id:
            customer = stripe.Customer.retrieve(self.customer_id)
        else:
            existing_customers = stripe.Customer.list(email=self.customer_email).data
            if existing_customers:
                customer = existing_customers[0]
            else:
                customer = stripe.Customer.create(description=self.customer_description, email=self.customer_email)

        self.customer_id = customer.id
        return self.customer_id

    @staticmethod
    def retrieve_session(session_id) -> stripe.checkout.Session:
        """
        Retrieve a Stripe checkout session object expanded to include the line_items.

        Stripe API Reference: https://stripe.com/docs/api/checkout/sessions/object

        Args:
            session_id (str): A Stripe session ID, ex: cs_test_ABCDEG

        Returns:
            stripe.checkout.Session: The session obj
        """
        return stripe.checkout.Session.retrieve(session_id, expand=["line_items"])

    @staticmethod
    def retrieve_subscription(subscription_id) -> stripe.Subscription:
        return stripe.Subscription.retrieve(subscription_id)

    @staticmethod
    def cancel_subscription(subscription_id) -> stripe.Subscription:
        return stripe.Subscription.delete(subscription_id)

    @staticmethod
    def caclulate_amount_with_discount(subscription):
        total_amount = 0

        for item in subscription["items"]["data"]:
            unit_amount = item["price"]["unit_amount"]
            total_amount += unit_amount

        if subscription.get("discount"):
            discount = subscription["discount"]["coupon"]

            if discount["amount_off"]:
                total_amount -= discount["amount_off"]
            elif discount["percent_off"]:
                total_amount *= 1 - discount["percent_off"] / 100.0

        return f"{total_amount / 100.0:.2f}"


class PremiumManager:
    @staticmethod
    def create_order(session_id):
        try:
            session = StripeManager.retrieve_session(session_id)

            session_id = session["id"]
            subscription_id = session["subscription"]
            product_id = session["line_items"]["data"][0]["price"]["product"]
            customer_id = session["customer"]
            amount_total = session["amount_total"] / 100

            user = StripeCustomer.objects.get(customer_id=customer_id)

            payment_history = PaymentHistory.objects.create(
                stripe_customer=user,
                subscription_id=subscription_id,
                session_id=session_id,
                product=Product.PREMIUM_YEARLY,
                product_id=product_id,
                status=PaymentStatus.AWAITING_PAYMENT,
                amount_total=amount_total,
            )

            return payment_history
        except Exception as e:
            logger.error(f"An error occurred while creating the order: {str(e)}")

    @staticmethod
    def fulfill_order(session):
        try:
            session_id = session["id"]
            customer_id = session["customer"]
            subscription_id = session["subscription"]

            payment_history = PaymentHistory.objects.get(session_id=session_id)
            payment_history.status = PaymentStatus.PAID
            payment_history.save()

            stripe_customer = StripeCustomer.objects.get(customer_id=customer_id)
            stripe_customer.has_active_subscription = True
            stripe_customer.current_subscription_id = subscription_id
            stripe_customer.last_subscription_id = subscription_id
            stripe_customer.save()
        except Exception as e:
            logger.error(f"An error occurred while fulfilling the order: {str(e)}")

    @staticmethod
    def fail_order(session):
        try:
            session_id = session["id"]
            customer_id = session["customer"]

            payment_history = PaymentHistory.objects.get(session_id=session_id)
            payment_history.status = PaymentStatus.FAILED
            payment_history.save()

            stripe_customer = StripeCustomer.objects.get(customer_id=customer_id)
            stripe_customer.has_active_subscription = False
            stripe_customer.current_subscription_id = None
            stripe_customer.last_subscription_id = None
            stripe_customer.save()
        except Exception as e:
            logger.error(f"An error occurred while failing the order: {str(e)}")

    @staticmethod
    def canceled_subscription(subscription):
        try:
            subscription_id = subscription["id"]
            customer_id = subscription["customer"]
            ended_at = subscription["ended_at"]

            subscription = stripe.Subscription.retrieve(subscription_id)

            stripe_customer = StripeCustomer.objects.get(customer_id=customer_id)
            stripe_customer.has_active_subscription = False
            stripe_customer.current_subscription_id = None
            stripe_customer.last_subscription_id = subscription_id

            stripe_customer.premium_until = timezone.make_aware(
                datetime.fromtimestamp(subscription.current_period_end)
            )
            stripe_customer.ended_at = timezone.make_aware(datetime.fromtimestamp(ended_at))
            stripe_customer.save()
        except Exception as e:
            logger.error(f"An error occurred while canceling the subscription: {str(e)}")
