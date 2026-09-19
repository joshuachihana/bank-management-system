from django.contrib import admin

from .models import Account, AccountType, Beneficiary, Branch, Card


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("id", "branch_code", "branch_name", "city")
    search_fields = ("branch_code", "branch_name", "city")


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "interest_rate")
    search_fields = ("name",)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "account_number", "customer", "branch", "account_type", "available_balance", "status")
    list_filter = ("status", "branch", "account_type")
    search_fields = ("account_number", "customer__user__username", "customer__national_id")


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "card_type", "status", "expiry_date")
    list_filter = ("card_type", "status")
    search_fields = ("card_number", "account__account_number")


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "beneficiary_name", "account_number", "bank_name")
    search_fields = ("beneficiary_name", "account_number", "bank_name", "customer__user__username")
