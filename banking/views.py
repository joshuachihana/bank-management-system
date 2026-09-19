from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from transactions.serializers import TransactionSerializer
from users.permissions import (
    IsActiveAuthenticated,
    IsManagementStaffOrReadOnly,
    IsOperationsStaff,
    is_customer,
    is_operations_role,
)
from users.services import write_audit_log

from .models import Account, AccountType, Beneficiary, Branch, Card
from .serializers import (
    AccountBalanceOperationSerializer,
    AccountSerializer,
    AccountTypeSerializer,
    BeneficiarySerializer,
    BranchSerializer,
    CardSerializer,
    TransferSerializer,
)


# ============================================================
# BRANCH
# ============================================================

class BranchListCreateAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get(self, request):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "CREATE",
            "branches",
            instance.pk,
            "Created branch."
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class BranchDetailAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get_object(self, pk):
        return Branch.objects.get(pk=pk)

    def get(self, request, pk):
        try:
            branch = self.get_object(pk)
        except Branch.DoesNotExist:
            return Response(
                {"detail": "Branch not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BranchSerializer(branch)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            branch = self.get_object(pk)
        except Branch.DoesNotExist:
            return Response(
                {"detail": "Branch not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BranchSerializer(
            branch,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "branches",
            instance.pk,
            "Updated branch."
        )

        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            branch = self.get_object(pk)
        except Branch.DoesNotExist:
            return Response(
                {"detail": "Branch not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BranchSerializer(
            branch,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "branches",
            instance.pk,
            "Updated branch."
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            branch = self.get_object(pk)
        except Branch.DoesNotExist:
            return Response(
                {"detail": "Branch not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        branch_id = branch.pk
        branch.delete()

        write_audit_log(
            request,
            "DELETE",
            "branches",
            branch_id,
            "Deleted branch."
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================================
# ACCOUNT TYPE
# ============================================================

class AccountTypeListCreateAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get(self, request):
        account_types = AccountType.objects.all()
        serializer = AccountTypeSerializer(
            account_types,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = AccountTypeSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "CREATE",
            "account_types",
            instance.pk,
            "Created account type."
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class AccountTypeDetailAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get_object(self, pk):
        return AccountType.objects.get(pk=pk)

    def get(self, request, pk):
        try:
            account_type = self.get_object(pk)
        except AccountType.DoesNotExist:
            return Response(
                {"detail": "Account type not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccountTypeSerializer(account_type)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            account_type = self.get_object(pk)
        except AccountType.DoesNotExist:
            return Response(
                {"detail": "Account type not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccountTypeSerializer(
            account_type,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "account_types",
            instance.pk,
            "Updated account type."
        )

        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            account_type = self.get_object(pk)
        except AccountType.DoesNotExist:
            return Response(
                {"detail": "Account type not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccountTypeSerializer(
            account_type,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "account_types",
            instance.pk,
            "Updated account type."
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            account_type = self.get_object(pk)
        except AccountType.DoesNotExist:
            return Response(
                {"detail": "Account type not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        account_type_id = account_type.pk
        account_type.delete()

        write_audit_log(
            request,
            "DELETE",
            "account_types",
            account_type_id,
            "Deleted account type."
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================================
# ACCOUNT
# ============================================================

class AccountListCreateAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get_queryset(self):
        queryset = Account.objects.select_related(
            "customer",
            "customer__user",
            "branch",
            "account_type"
        )

        if is_customer(self.request.user):
            return queryset.filter(
                customer__user=self.request.user
            )

        return queryset

    def get(self, request):
        accounts = self.get_queryset()
        serializer = AccountSerializer(
            accounts,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = AccountSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "CREATE",
            "accounts",
            instance.pk,
            "Created account."
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class AccountDetailAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get_queryset(self):
        queryset = Account.objects.select_related(
            "customer",
            "customer__user",
            "branch",
            "account_type"
        )

        if is_customer(self.request.user):
            return queryset.filter(
                customer__user=self.request.user
            )

        return queryset

    def get_object(self, pk):
        return self.get_queryset().get(pk=pk)

    def get(self, request, pk):
        try:
            account = self.get_object(pk)
        except Account.DoesNotExist:
            return Response(
                {"detail": "Account not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccountSerializer(account)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            account = self.get_object(pk)
        except Account.DoesNotExist:
            return Response(
                {"detail": "Account not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccountSerializer(
            account,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "accounts",
            instance.pk,
            "Updated account."
        )

        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            account = self.get_object(pk)
        except Account.DoesNotExist:
            return Response(
                {"detail": "Account not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccountSerializer(
            account,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "accounts",
            instance.pk,
            "Updated account."
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            account = self.get_object(pk)
        except Account.DoesNotExist:
            return Response(
                {"detail": "Account not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        account_id = account.pk
        account.delete()

        write_audit_log(
            request,
            "DELETE",
            "accounts",
            account_id,
            "Deleted account."
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================================
# DEPOSIT
# ============================================================

class AccountDepositAPIView(APIView):
    permission_classes = [IsOperationsStaff]

    def post(self, request, pk):
        try:
            account = Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return Response(
                {"detail": "Account not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccountBalanceOperationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        transaction_record = serializer.save(
            account=account,
            operation="deposit"
        )

        write_audit_log(
            request,
            "CREATE",
            "transactions",
            transaction_record.pk,
            "Deposited funds."
        )

        return Response(
            TransactionSerializer(transaction_record).data,
            status=status.HTTP_201_CREATED
        )


# ============================================================
# WITHDRAW
# ============================================================

class AccountWithdrawAPIView(APIView):
    permission_classes = [IsOperationsStaff]

    def post(self, request, pk):
        try:
            account = Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return Response(
                {"detail": "Account not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccountBalanceOperationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        transaction_record = serializer.save(
            account=account,
            operation="withdraw"
        )

        write_audit_log(
            request,
            "CREATE",
            "transactions",
            transaction_record.pk,
            "Withdrew funds."
        )

        return Response(
            TransactionSerializer(transaction_record).data,
            status=status.HTTP_201_CREATED
        )


# ============================================================
# TRANSFER
# ============================================================

class TransferAPIView(APIView):
    permission_classes = [IsActiveAuthenticated]

    def post(self, request):
        serializer = TransferSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        if (
            is_customer(request.user)
            and serializer.validated_data[
                "source_account"
            ].customer.user != request.user
        ):
            return Response(
                {
                    "detail": (
                        "You cannot transfer from another "
                        "customer's account."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        transaction_record = serializer.save()

        write_audit_log(
            request,
            "CREATE",
            "transactions",
            transaction_record.pk,
            "Transferred funds."
        )

        return Response(
            TransactionSerializer(transaction_record).data,
            status=status.HTTP_201_CREATED
        )


# ============================================================
# CARD
# ============================================================

class CardListCreateAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get_queryset(self):
        queryset = Card.objects.select_related(
            "account",
            "account__customer",
            "account__customer__user"
        )

        if is_customer(self.request.user):
            return queryset.filter(
                account__customer__user=self.request.user
            )

        return queryset

    def get(self, request):
        cards = self.get_queryset()
        serializer = CardSerializer(
            cards,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = CardSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "CREATE",
            "cards",
            instance.pk,
            "Created card."
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class CardDetailAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get_queryset(self):
        queryset = Card.objects.select_related(
            "account",
            "account__customer",
            "account__customer__user"
        )

        if is_customer(self.request.user):
            return queryset.filter(
                account__customer__user=self.request.user
            )

        return queryset

    def get_object(self, pk):
        return self.get_queryset().get(pk=pk)

    def get(self, request, pk):
        try:
            card = self.get_object(pk)
        except Card.DoesNotExist:
            return Response(
                {"detail": "Card not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CardSerializer(card)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            card = self.get_object(pk)
        except Card.DoesNotExist:
            return Response(
                {"detail": "Card not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CardSerializer(
            card,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "cards",
            instance.pk,
            "Updated card."
        )

        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            card = self.get_object(pk)
        except Card.DoesNotExist:
            return Response(
                {"detail": "Card not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CardSerializer(
            card,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "cards",
            instance.pk,
            "Updated card."
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            card = self.get_object(pk)
        except Card.DoesNotExist:
            return Response(
                {"detail": "Card not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        card_id = card.pk
        card.delete()

        write_audit_log(
            request,
            "DELETE",
            "cards",
            card_id,
            "Deleted card."
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================================
# BENEFICIARY
# ============================================================

class BeneficiaryListCreateAPIView(APIView):
    permission_classes = [IsActiveAuthenticated]

    def get_queryset(self):
        queryset = Beneficiary.objects.select_related(
            "customer",
            "customer__user"
        )

        if is_customer(self.request.user):
            return queryset.filter(
                customer__user=self.request.user
            )

        return queryset

    def get(self, request):
        beneficiaries = self.get_queryset()
        serializer = BeneficiarySerializer(
            beneficiaries,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = BeneficiarySerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        if (
            is_customer(request.user)
            and not is_operations_role(request.user)
        ):
            instance = serializer.save(
                customer=request.user.customer
            )
        else:
            instance = serializer.save()

        write_audit_log(
            request,
            "CREATE",
            "beneficiaries",
            instance.pk,
            "Created beneficiary."
        )

        return Response(
            BeneficiarySerializer(instance).data,
            status=status.HTTP_201_CREATED
        )


class BeneficiaryDetailAPIView(APIView):
    permission_classes = [IsActiveAuthenticated]

    def get_queryset(self):
        queryset = Beneficiary.objects.select_related(
            "customer",
            "customer__user"
        )

        if is_customer(self.request.user):
            return queryset.filter(
                customer__user=self.request.user
            )

        return queryset

    def get_object(self, pk):
        return self.get_queryset().get(pk=pk)

    def get(self, request, pk):
        try:
            beneficiary = self.get_object(pk)
        except Beneficiary.DoesNotExist:
            return Response(
                {"detail": "Beneficiary not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BeneficiarySerializer(beneficiary)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            beneficiary = self.get_object(pk)
        except Beneficiary.DoesNotExist:
            return Response(
                {"detail": "Beneficiary not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BeneficiarySerializer(
            beneficiary,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "beneficiaries",
            instance.pk,
            "Updated beneficiary."
        )

        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            beneficiary = self.get_object(pk)
        except Beneficiary.DoesNotExist:
            return Response(
                {"detail": "Beneficiary not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BeneficiarySerializer(
            beneficiary,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        write_audit_log(
            request,
            "UPDATE",
            "beneficiaries",
            instance.pk,
            "Updated beneficiary."
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            beneficiary = self.get_object(pk)
        except Beneficiary.DoesNotExist:
            return Response(
                {"detail": "Beneficiary not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        beneficiary_id = beneficiary.pk
        beneficiary.delete()

        write_audit_log(
            request,
            "DELETE",
            "beneficiaries",
            beneficiary_id,
            "Deleted beneficiary."
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )