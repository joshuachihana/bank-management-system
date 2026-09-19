from django.contrib import admin

from .models import JournalEntry, Transaction, TransactionType


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class JournalEntryInline(admin.TabularInline):
    model = JournalEntry
    extra = 0


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "reference", "transaction_type", "status", "created_at")
    list_filter = ("status", "transaction_type")
    search_fields = ("reference", "description")
    inlines = [JournalEntryInline]


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "transaction", "account", "entry_type", "amount")
    list_filter = ("entry_type",)
    search_fields = ("transaction__reference", "account__account_number")
