from django.contrib import admin

from langcorrect.subscriptions.models import PaymentHistory, StripeCustomer


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    pass
