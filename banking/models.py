from django.db import models


class Branch(models.Model):
    branch_code = models.CharField(
        max_length=10,
        unique=True
    )

    branch_name = models.CharField(
        max_length=100
    )

    address = models.CharField(
        max_length=255,
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        db_table = "branches"
        ordering = ["branch_name"]

    def __str__(self):
        return f"{self.branch_name} ({self.branch_code})"



class AccountType(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )

    description = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "account_types"
        ordering = ["name"]

    def __str__(self):
        return self.name



from django.utils import timezone


class Account(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("FROZEN", "Frozen"),
        ("CLOSED", "Closed"),
    ]

    customer = models.ForeignKey(
        "users.Customer",
        on_delete=models.PROTECT,
        related_name="accounts"
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="accounts"
    )

    account_type = models.ForeignKey(
        AccountType,
        on_delete=models.PROTECT,
        related_name="accounts"
    )

    account_number = models.CharField(
        max_length=20,
        unique=True
    )

    ledger_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )

    available_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    opened_at = models.DateTimeField(
        default=timezone.now
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "accounts"
        ordering = ["account_number"]

    def __str__(self):
        return self.account_number


class Card(models.Model):

    CARD_TYPES = [
        ("DEBIT", "Debit Card"),
        ("CREDIT", "Credit Card"),
        ("ATM", "ATM Card"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("BLOCKED", "Blocked"),
        ("EXPIRED", "Expired"),
    ]

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="cards"
    )

    card_number = models.CharField(
        max_length=19,
        unique=True
    )

    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPES
    )

    expiry_date = models.DateField()

    cvv = models.CharField(
        max_length=4
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    class Meta:
        db_table = "cards"

    def __str__(self):
        return f"{self.card_type} - {self.card_number[-4:]}"


class Beneficiary(models.Model):

    customer = models.ForeignKey(
        "users.Customer",
        on_delete=models.CASCADE,
        related_name="beneficiaries"
    )

    beneficiary_name = models.CharField(
        max_length=150
    )

    account_number = models.CharField(
        max_length=20
    )

    bank_name = models.CharField(
        max_length=100
    )

    nickname = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        db_table = "beneficiaries"

    def __str__(self):
        return self.beneficiary_name
