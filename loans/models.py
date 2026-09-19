from django.db import models
from django.utils import timezone


class Loan(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("ACTIVE", "Active"),
        ("PAID", "Paid"),
    ]

    customer = models.ForeignKey(
        "users.Customer",
        on_delete=models.PROTECT,
        related_name="loans"
    )

    approved_by = models.ForeignKey(
        "users.Employee",
        on_delete=models.PROTECT,
        related_name="approved_loans",
        null=True,
        blank=True
    )

    principal = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    term_months = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        db_table = "loans"

    def __str__(self):
        return f"Loan #{self.pk}"


class LoanPayment(models.Model):

    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    transaction = models.OneToOneField(
        "transactions.Transaction",
        on_delete=models.PROTECT,
        related_name="loan_payment"
    )

    amount_principal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    amount_interest = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    payment_date = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        db_table = "loan_payments"

    def __str__(self):
        return f"Payment for Loan #{self.loan.id}"