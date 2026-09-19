from rest_framework import serializers

from .models import JournalEntry, Transaction, TransactionType


class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ["id", "name", "description"]


class JournalEntrySerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source="account.account_number", read_only=True)

    class Meta:
        model = JournalEntry
        fields = ["id", "transaction", "account", "account_number", "entry_type", "amount"]


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_name = serializers.CharField(source="transaction_type.name", read_only=True)
    journal_entries = JournalEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "reference",
            "transaction_type",
            "transaction_type_name",
            "description",
            "status",
            "created_at",
            "journal_entries",
        ]
        read_only_fields = ["reference", "status", "created_at", "journal_entries"]
