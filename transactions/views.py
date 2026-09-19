from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.permissions import IsManagementStaffOrReadOnly, is_customer

from .models import JournalEntry, Transaction, TransactionType
from .serializers import (
    JournalEntrySerializer,
    TransactionSerializer,
    TransactionTypeSerializer,
)


class TransactionTypeListCreateAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get(self, request):
        transaction_types = TransactionType.objects.all()
        serializer = TransactionTypeSerializer(transaction_types, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = TransactionTypeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TransactionTypeDetailAPIView(APIView):
    permission_classes = [IsManagementStaffOrReadOnly]

    def get_object(self, pk):
        try:
            return TransactionType.objects.get(pk=pk)
        except TransactionType.DoesNotExist:
            return None

    def get(self, request, pk):
        transaction_type = self.get_object(pk)

        if not transaction_type:
            return Response(
                {"detail": "Transaction type not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TransactionTypeSerializer(transaction_type)

        return Response(serializer.data)

    def put(self, request, pk):
        transaction_type = self.get_object(pk)

        if not transaction_type:
            return Response(
                {"detail": "Transaction type not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TransactionTypeSerializer(
            transaction_type,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        transaction_type = self.get_object(pk)

        if not transaction_type:
            return Response(
                {"detail": "Transaction type not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TransactionTypeSerializer(
            transaction_type,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        transaction_type = self.get_object(pk)

        if not transaction_type:
            return Response(
                {"detail": "Transaction type not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        transaction_type.delete()

        return Response(
            {"detail": "Transaction type deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class TransactionListAPIView(APIView):
    def get(self, request):
        queryset = Transaction.objects.select_related(
            "transaction_type"
        ).prefetch_related(
            "journal_entries",
            "journal_entries__account",
        )

        if is_customer(request.user):
            queryset = queryset.filter(
                journal_entries__account__customer__user=request.user
            ).distinct()

        serializer = TransactionSerializer(queryset, many=True)

        return Response(serializer.data)


class TransactionDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Transaction.objects.select_related(
                "transaction_type"
            ).prefetch_related(
                "journal_entries",
                "journal_entries__account",
            ).get(pk=pk)

        except Transaction.DoesNotExist:
            return None

    def get(self, request, pk):
        transaction = self.get_object(pk)

        if not transaction:
            return Response(
                {"detail": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if is_customer(request.user):
            if not transaction.journal_entries.filter(
                account__customer__user=request.user
            ).exists():
                return Response(
                    {"detail": "Transaction not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = TransactionSerializer(transaction)

        return Response(serializer.data)


class JournalEntryListAPIView(APIView):
    def get(self, request):
        queryset = JournalEntry.objects.select_related(
            "transaction",
            "account",
            "account__customer",
        )

        if is_customer(request.user):
            queryset = queryset.filter(
                account__customer__user=request.user
            )

        serializer = JournalEntrySerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)


class JournalEntryDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return JournalEntry.objects.select_related(
                "transaction",
                "account",
                "account__customer",
            ).get(pk=pk)

        except JournalEntry.DoesNotExist:
            return None

    def get(self, request, pk):
        journal_entry = self.get_object(pk)

        if not journal_entry:
            return Response(
                {"detail": "Journal entry not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if is_customer(request.user):
            if journal_entry.account.customer.user != request.user:
                return Response(
                    {"detail": "Journal entry not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = JournalEntrySerializer(journal_entry)

        return Response(serializer.data)