from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from users.models import Customer, Role

from .models import Account, AccountType, Branch


User = get_user_model()


class TransferApiTests(APITestCase):
    def setUp(self):
        customer_role = Role.objects.create(name="Customer")
        self.user = User.objects.create_user(
            username="alice",
            password="Customer@12345",
            role=customer_role,
            status="ACTIVE",
        )
        self.customer = Customer.objects.create(user=self.user, national_id="NID-1")
        other_user = User.objects.create_user(
            username="bob",
            password="Customer@12345",
            role=customer_role,
            status="ACTIVE",
        )
        self.other_customer = Customer.objects.create(user=other_user, national_id="NID-2")
        branch = Branch.objects.create(branch_code="BR1", branch_name="Main")
        account_type = AccountType.objects.create(name="Checking")
        self.source = Account.objects.create(
            customer=self.customer,
            branch=branch,
            account_type=account_type,
            account_number="1001",
            ledger_balance=Decimal("100.00"),
            available_balance=Decimal("100.00"),
        )
        self.destination = Account.objects.create(
            customer=self.other_customer,
            branch=branch,
            account_type=account_type,
            account_number="1002",
            ledger_balance=Decimal("50.00"),
            available_balance=Decimal("50.00"),
        )
        self.client.force_authenticate(self.user)

    def test_customer_can_transfer_from_own_account(self):
        response = self.client.post(
            "/api/banking/transfers/",
            {
                "source_account": self.source.pk,
                "destination_account": self.destination.pk,
                "amount": "25.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.source.refresh_from_db()
        self.destination.refresh_from_db()
        self.assertEqual(self.source.available_balance, Decimal("75.00"))
        self.assertEqual(self.destination.available_balance, Decimal("75.00"))

    def test_customer_cannot_transfer_from_other_account(self):
        response = self.client.post(
            "/api/banking/transfers/",
            {
                "source_account": self.destination.pk,
                "destination_account": self.source.pk,
                "amount": "25.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
