# ruff: noqa: ERA001
from django.contrib import admin

from langcorrect.subscriptions.models import PaymentHistory
from langcorrect.subscriptions.models import StripeCustomer

# class ReadOnlyAdmin(admin.ModelAdmin):
#     def has_delete_permission(self, request, obj=None):
#         return False

#     def get_readonly_fields(self, request, obj=None):
#         return [f.name for f in self.model._meta.fields]

#     def has_add_permission(self, request):
#         return False


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "has_active_subscription",
        "customer_id",
        "current_subscription_id",
        "created",
        "modified",
    ]
    search_fields = ["user__username", "customer_id", "current_subscription_id"]


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "stripe_customer",
        "subscription_id",
        "product_id",
        "product",
        "status",
        "amount_total",
        "has_used_coupon",
    ]
    search_fields = ["stripe_customer__user__username", "subscription_id"]
