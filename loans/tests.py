from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from users.models import Customer, Role

from .models import Loan


User = get_user_model()


class LoanApiTests(APITestCase):
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
        self.client.force_authenticate(self.user)

    def test_customer_loan_application_uses_authenticated_customer(self):
        response = self.client.post(
            "/api/loans/loans/",
            {
                "customer": self.other_customer.pk,
                "principal": "1000.00",
                "interest_rate": "5.50",
                "term_months": 12,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        loan = Loan.objects.get()
        self.assertEqual(loan.customer, self.customer)
        self.assertEqual(loan.principal, Decimal("1000.00"))
