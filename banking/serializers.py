from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from transactions.models import JournalEntry, Transaction, TransactionType
from users.models import Customer

from .models import Account, AccountType, Beneficiary, Branch, Card


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["id", "branch_code", "branch_name", "address", "city"]


class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ["id", "name", "interest_rate", "description"]


class AccountSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.user.get_full_name", read_only=True)
    branch_name = serializers.CharField(source="branch.branch_name", read_only=True)
    account_type_name = serializers.CharField(source="account_type.name", read_only=True)

    class Meta:
        model = Account+
        
        fields = [
            "id",
            "customer",
            "customer_name",
            "branch",
            "branch_name",
            "account_type",
            "account_type_name",
            "account_number",
            "ledger_balance",
            "available_balance",
            "status",
            "opened_at",
            "closed_at",
        ]
        read_only_fields = ["ledger_balance", "available_balance", "opened_at", "closed_at"]


class CardSerializer(serializers.ModelSerializer):
    masked_card_number = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = [
            "id",
            "account",
            "masked_card_number",
            "card_number",
            "card_type",
            "expiry_date",
            "cvv",
            "status",
        ]
        extra_kwargs = {
            "card_number": {"write_only": True},
            "cvv": {"write_only": True},
        }

    def get_masked_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}"


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = [
            "id",
            "customer",
            "beneficiary_name",
            "account_number",
            "bank_name",
            "nickname",
        ]


class MoneyMovementSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal("0.01"))
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)


class TransferSerializer(MoneyMovementSerializer):
    source_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    destination_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    def validate(self, attrs):
        source = attrs["source_account"]
        destination = attrs["destination_account"]
        amount = attrs["amount"]

        if source.pk == destination.pk:
            raise serializers.ValidationError("Source and destination accounts must be different.")
        if source.status != "ACTIVE" or destination.status != "ACTIVE":
            raise serializers.ValidationError("Both accounts must be active.")
        if source.available_balance < amount:
            raise serializers.ValidationError("Insufficient available balance.")
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        source = Account.objects.select_for_update().get(pk=self.validated_data["source_account"].pk)
        destination = Account.objects.select_for_update().get(pk=self.validated_data["destination_account"].pk)
        amount = self.validated_data["amount"]
        description = self.validated_data.get("description") or "Internal transfer"

        if source.available_balance < amount:
            raise serializers.ValidationError("Insufficient available balance.")

        transaction_type, _ = TransactionType.objects.get_or_create(
            name="Transfer",
            defaults={"description": "Internal account transfer"},
        )
        transaction_record = Transaction.objects.create(
            reference=f"TRF-{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
            transaction_type=transaction_type,
            description=description,
            status="COMPLETED",
        )

        source.ledger_balance -= amount
        source.available_balance -= amount
        source.save(update_fields=["ledger_balance", "available_balance"])

        destination.ledger_balance += amount
        destination.available_balance += amount
        destination.save(update_fields=["ledger_balance", "available_balance"])

        JournalEntry.objects.bulk_create(
            [
                JournalEntry(
                    transaction=transaction_record,
                    account=source,
                    entry_type="DEBIT",
                    amount=amount,
                ),
                JournalEntry(
                    transaction=transaction_record,
                    account=destination,
                    entry_type="CREDIT",
                    amount=amount,
                ),
            ]
        )

        return transaction_record


class AccountBalanceOperationSerializer(MoneyMovementSerializer):
    def save(self, account, operation):
        amount = self.validated_data["amount"]
        description = self.validated_data.get("description") or operation.title()

        with transaction.atomic():
            locked_account = Account.objects.select_for_update().get(pk=account.pk)
            if locked_account.status != "ACTIVE":
                raise serializers.ValidationError("Account must be active.")
            if operation == "withdraw" and locked_account.available_balance < amount:
                raise serializers.ValidationError("Insufficient available balance.")

            transaction_type, _ = TransactionType.objects.get_or_create(
                name=operation.title(),
                defaults={"description": f"Account {operation}"},
            )
            transaction_record = Transaction.objects.create(
                reference=f"{operation[:3].upper()}-{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
                transaction_type=transaction_type,
                description=description,
                status="COMPLETED",
            )

            if operation == "deposit":
                locked_account.ledger_balance += amount
                locked_account.available_balance += amount
                entry_type = "CREDIT"
            else:
                locked_account.ledger_balance -= amount
                locked_account.available_balance -= amount
                entry_type = "DEBIT"

            locked_account.save(update_fields=["ledger_balance", "available_balance"])
            JournalEntry.objects.create(
                transaction=transaction_record,
                account=locked_account,
                entry_type=entry_type,
                amount=amount,
            )
            return transaction_record
