from django.db import models


class TransactionType(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "transaction_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


from django.utils import timezone


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("REVERSED", "Reversed"),
    ]

    reference = models.CharField(
        max_length=40,
        unique=True
    )

    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return self.reference


class JournalEntry(models.Model):
    ENTRY_CHOICES = [
        ("DEBIT", "Debit"),
        ("CREDIT", "Credit"),
    ]

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="journal_entries"
    )

    account = models.ForeignKey(
        "banking.Account",
        on_delete=models.PROTECT,
        related_name="journal_entries"
    )

    entry_type = models.CharField(
        max_length=10,
        choices=ENTRY_CHOICES
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    class Meta:
        db_table = "journal_entries"

    def __str__(self):
        return (
            f"{self.transaction.reference} - "
            f"{self.entry_type} {self.amount}"
        )