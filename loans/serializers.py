from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from banking.models import Account
from transactions.models import JournalEntry, Transaction, TransactionType
from users.permissions import is_operations_role

from .models import Loan, LoanPayment


class LoanSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.user.get_full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.user.get_full_name", read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id",
            "customer",
            "customer_name",
            "approved_by",
            "approved_by_name",
            "principal",
            "interest_rate",
            "term_months",
            "status",
            "approved_at",
            "created_at",
        ]
        read_only_fields = ["approved_by", "status", "approved_at", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and not is_operations_role(request.user):
            validated_data["customer"] = request.user.customer
        return super().create(validated_data)


class LoanDecisionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["APPROVED", "REJECTED"])


class LoanPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanPayment
        fields = [
            "id",
            "loan",
            "transaction",
            "amount_principal",
            "amount_interest",
            "payment_date",
        ]
        read_only_fields = ["transaction", "payment_date"]


class CreateLoanPaymentSerializer(serializers.Serializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    amount_principal = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )
    amount_interest = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )

    def validate(self, attrs):
        amount = attrs["amount_principal"] + attrs["amount_interest"]
        account = attrs["account"]
        if amount <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")
        if account.status != "ACTIVE":
            raise serializers.ValidationError("Payment account must be active.")
        if account.available_balance < amount:
            raise serializers.ValidationError("Insufficient available balance.")
        return attrs

    @transaction.atomic
    def save(self, loan):
        account = Account.objects.select_for_update().get(pk=self.validated_data["account"].pk)
        amount_principal = self.validated_data["amount_principal"]
        amount_interest = self.validated_data["amount_interest"]
        total_amount = amount_principal + amount_interest

        if account.available_balance < total_amount:
            raise serializers.ValidationError("Insufficient available balance.")

        transaction_type, _ = TransactionType.objects.get_or_create(
            name="Loan Payment",
            defaults={"description": "Loan repayment"},
        )
        transaction_record = Transaction.objects.create(
            reference=f"LOP-{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
            transaction_type=transaction_type,
            description=f"Loan payment for loan #{loan.pk}",
            status="COMPLETED",
        )

        account.ledger_balance -= total_amount
        account.available_balance -= total_amount
        account.save(update_fields=["ledger_balance", "available_balance"])

        JournalEntry.objects.create(
            transaction=transaction_record,
            account=account,
            entry_type="DEBIT",
            amount=total_amount,
        )

        payment = LoanPayment.objects.create(
            loan=loan,
            transaction=transaction_record,
            amount_principal=amount_principal,
            amount_interest=amount_interest,
        )

        if not loan.payments.exclude(pk=payment.pk).exists():
            loan.status = "ACTIVE"
            loan.save(update_fields=["status"])

        return payment
