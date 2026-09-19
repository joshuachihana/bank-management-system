from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Role


User = get_user_model()


class JwtLoginTests(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Customer")
        self.user = User.objects.create_user(
            username="customer1",
            password="Customer@12345",
            role=self.role,
            status="ACTIVE",
        )

    def test_active_user_can_login(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "customer1", "password": "Customer@12345"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["username"], "customer1")

    def test_locked_user_cannot_login(self):
        self.user.status = "LOCKED"
        self.user.save(update_fields=["status"])

        response = self.client.post(
            "/api/auth/login/",
            {"username": "customer1", "password": "Customer@12345"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
