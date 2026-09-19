from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from notifications.models import Notification
from users.permissions import (
    IsActiveAuthenticated,
    IsOperationsStaff,
    is_customer,
)
from users.services import write_audit_log

from .models import Loan, LoanPayment
from .serializers import (
    CreateLoanPaymentSerializer,
    LoanDecisionSerializer,
    LoanPaymentSerializer,
    LoanSerializer,
)


# ============================================================
# LOAN LIST + CREATE
# ============================================================

class LoanListCreateAPIView(APIView):
    permission_classes = [IsActiveAuthenticated]

    def get_queryset(self):
        queryset = Loan.objects.select_related(
            "customer",
            "customer__user",
            "approved_by",
            "approved_by__user",
        )

        if is_customer(self.request.user):
            queryset = queryset.filter(
                customer__user=self.request.user
            )

        return queryset

    def get(self, request):
        loans = self.get_queryset()
        serializer = LoanSerializer(loans, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = LoanSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        loan = serializer.save()

        write_audit_log(
            request,
            "CREATE",
            "loans",
            loan.pk,
            "Created loan application.",
        )

        return Response(
            LoanSerializer(loan).data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# LOAN DETAIL
# ============================================================

class LoanDetailAPIView(APIView):
    permission_classes = [IsActiveAuthenticated]

    def get_queryset(self):
        queryset = Loan.objects.select_related(
            "customer",
            "customer__user",
            "approved_by",
            "approved_by__user",
        )

        if is_customer(self.request.user):
            queryset = queryset.filter(
                customer__user=self.request.user
            )

        return queryset

    def get_object(self, pk):
        try:
            return self.get_queryset().get(pk=pk)
        except Loan.DoesNotExist:
            return None

    def get(self, request, pk):
        loan = self.get_object(pk)

        if loan is None:
            return Response(
                {"detail": "Loan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LoanSerializer(loan)

        return Response(serializer.data)

    def put(self, request, pk):
        # Only operations staff can update
        permission = IsOperationsStaff()

        if not permission.has_permission(request, self):
            return Response(
                {"detail": "You do not have permission to update loans."},
                status=status.HTTP_403_FORBIDDEN,
            )

        loan = self.get_object(pk)

        if loan is None:
            return Response(
                {"detail": "Loan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LoanSerializer(
            loan,
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        loan = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "loans",
            loan.pk,
            "Updated loan.",
        )

        return Response(
            LoanSerializer(loan).data
        )

    def patch(self, request, pk):
        # Only operations staff can update
        permission = IsOperationsStaff()

        if not permission.has_permission(request, self):
            return Response(
                {"detail": "You do not have permission to update loans."},
                status=status.HTTP_403_FORBIDDEN,
            )

        loan = self.get_object(pk)

        if loan is None:
            return Response(
                {"detail": "Loan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LoanSerializer(
            loan,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        loan = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "loans",
            loan.pk,
            "Updated loan.",
        )

        return Response(
            LoanSerializer(loan).data
        )

    def delete(self, request, pk):
        # Only operations staff can delete
        permission = IsOperationsStaff()

        if not permission.has_permission(request, self):
            return Response(
                {"detail": "You do not have permission to delete loans."},
                status=status.HTTP_403_FORBIDDEN,
            )

        loan = self.get_object(pk)

        if loan is None:
            return Response(
                {"detail": "Loan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        loan_id = loan.pk

        loan.delete()

        write_audit_log(
            request,
            "DELETE",
            "loans",
            loan_id,
            "Deleted loan.",
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================================
# LOAN DECISION
# ============================================================

class LoanDecisionAPIView(APIView):
    permission_classes = [IsOperationsStaff]

    def post(self, request, pk):
        try:
            loan = Loan.objects.select_related(
                "customer",
                "customer__user",
                "approved_by",
                "approved_by__user",
            ).get(pk=pk)

        except Loan.DoesNotExist:
            return Response(
                {"detail": "Loan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LoanDecisionSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        decision = serializer.validated_data["status"]

        employee = getattr(
            request.user,
            "employee",
            None,
        )

        if decision == "APPROVED" and employee is None:
            return Response(
                {
                    "detail": (
                        "Approving user must be an employee."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        loan.status = decision

        if decision == "APPROVED":
            loan.approved_by = employee
            loan.approved_at = timezone.now()

            loan.save(
                update_fields=[
                    "status",
                    "approved_by",
                    "approved_at",
                ]
            )

        else:
            loan.save(
                update_fields=["status"]
            )

        Notification.objects.create(
            customer=loan.customer,
            title=f"Loan {loan.status.lower()}",
            message=(
                f"Your loan application #{loan.pk} "
                f"has been {loan.status.lower()}."
            ),
        )

        write_audit_log(
            request,
            "UPDATE",
            "loans",
            loan.pk,
            f"Loan {loan.status.lower()}.",
        )

        return Response(
            LoanSerializer(loan).data
        )


# ============================================================
# LOAN PAYMENT
# ============================================================

class LoanPayAPIView(APIView):
    permission_classes = [IsActiveAuthenticated]

    def post(self, request, pk):
        try:
            loan = Loan.objects.get(pk=pk)

        except Loan.DoesNotExist:
            return Response(
                {"detail": "Loan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CreateLoanPaymentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        account = serializer.validated_data["account"]

        # Customers can only pay from their own account
        if (
            is_customer(request.user)
            and account.customer.user != request.user
        ):
            return Response(
                {
                    "detail": (
                        "You cannot pay from another "
                        "customer's account."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        payment = serializer.save(
            loan=loan
        )

        write_audit_log(
            request,
            "CREATE",
            "loan_payments",
            payment.pk,
            "Created loan payment.",
        )

        return Response(
            LoanPaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# LOAN PAYMENT LIST
# ============================================================

class LoanPaymentListAPIView(APIView):
    permission_classes = [IsActiveAuthenticated]

    def get_queryset(self):
        queryset = LoanPayment.objects.select_related(
            "loan",
            "loan__customer",
            "loan__customer__user",
            "transaction",
        )

        if is_customer(self.request.user):
            queryset = queryset.filter(
                loan__customer__user=self.request.user
            )

        return queryset

    def get(self, request):
        payments = self.get_queryset()

        serializer = LoanPaymentSerializer(
            payments,
            many=True,
        )

        return Response(serializer.data)


# ============================================================
# LOAN PAYMENT DETAIL
# ============================================================

class LoanPaymentDetailAPIView(APIView):
    permission_classes = [IsActiveAuthenticated]

    def get_queryset(self):
        queryset = LoanPayment.objects.select_related(
            "loan",
            "loan__customer",
            "loan__customer__user",
            "transaction",
        )

        if is_customer(self.request.user):
            queryset = queryset.filter(
                loan__customer__user=self.request.user
            )

        return queryset

    def get(self, request, pk):
        try:
            payment = self.get_queryset().get(pk=pk)

        except LoanPayment.DoesNotExist:
            return Response(
                {"detail": "Loan payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LoanPaymentSerializer(
            payment
        )

        return Response(serializer.data)