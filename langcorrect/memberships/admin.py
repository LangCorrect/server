from django.contrib import admin

from langcorrect.memberships.models import Membership


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "customer_code",
        "subscription_code",
        "plan_type",
        "billing_cycle_ends",
        "cancelled_date",
    ]
    list_filter = ["plan_type"]
    search_fields = [
        "plan_type",
        "user__username",
        "customer_code",
        "subscription_code",
    ]
