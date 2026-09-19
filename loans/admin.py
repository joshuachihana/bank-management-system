from django.contrib import admin

from .models import Loan, LoanPayment


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "principal", "interest_rate", "term_months", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("customer__user__username", "customer__national_id")


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "loan", "transaction", "amount_principal", "amount_interest", "payment_date")
    search_fields = ("loan__id", "transaction__reference")
