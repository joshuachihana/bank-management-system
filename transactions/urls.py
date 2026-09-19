from django.urls import path

from .views import (
    TransactionTypeListCreateAPIView,
    TransactionTypeDetailAPIView,
    TransactionListAPIView,
    TransactionDetailAPIView,
    JournalEntryListAPIView,
    JournalEntryDetailAPIView,
)


urlpatterns = [
    path(
        "transaction-types/",
        TransactionTypeListCreateAPIView.as_view(),
        name="transaction-type-list-create",
    ),

    path(
        "transaction-types/<int:pk>/",
        TransactionTypeDetailAPIView.as_view(),
        name="transaction-type-detail",
    ),

    path(
        "transactions/",
        TransactionListAPIView.as_view(),
        name="transaction-list",
    ),

    path(
        "transactions/<int:pk>/",
        TransactionDetailAPIView.as_view(),
        name="transaction-detail",
    ),

    path(
        "journal-entries/",
        JournalEntryListAPIView.as_view(),
        name="journal-entry-list",
    ),

    path(
        "journal-entries/<int:pk>/",
        JournalEntryDetailAPIView.as_view(),
        name="journal-entry-detail",
    ),
]