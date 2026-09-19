from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "roles"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users"
    )

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("LOCKED", "Locked"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username


class Customer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer"
    )

    national_id = models.CharField(
        max_length=30,
        unique=True
    )

    class Meta:
        db_table = "customers"

    def __str__(self):
        return self.user.get_full_name()


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee"
    )

    branch = models.ForeignKey(
        "banking.Branch",
        on_delete=models.PROTECT,
        related_name="employees"
    )

    position = models.CharField(max_length=100)

    class Meta:
        db_table = "employees"

    def __str__(self):
        return f"{self.position} - {self.user.username}"