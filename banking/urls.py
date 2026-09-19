from django.urls import path

from .views import (
    AccountDepositAPIView,
    AccountDetailAPIView,
    AccountListCreateAPIView,
    AccountTypeDetailAPIView,
    AccountTypeListCreateAPIView,
    AccountWithdrawAPIView,
    BeneficiaryDetailAPIView,
    BeneficiaryListCreateAPIView,
    BranchDetailAPIView,
    BranchListCreateAPIView,
    CardDetailAPIView,
    CardListCreateAPIView,
    TransferAPIView,
)


urlpatterns = [

    # Branches
    path(
        "branches/",
        BranchListCreateAPIView.as_view(),
        name="branch-list-create"
    ),

    path(
        "branches/<int:pk>/",
        BranchDetailAPIView.as_view(),
        name="branch-detail"
    ),


    # Account Types
    path(
        "account-types/",
        AccountTypeListCreateAPIView.as_view(),
        name="account-type-list-create"
    ),

    path(
        "account-types/<int:pk>/",
        AccountTypeDetailAPIView.as_view(),
        name="account-type-detail"
    ),


    # Accounts
    path(
        "accounts/",
        AccountListCreateAPIView.as_view(),
        name="account-list-create"
    ),

    path(
        "accounts/<int:pk>/",
        AccountDetailAPIView.as_view(),
        name="account-detail"
    ),


    # Account Operations
    path(
        "accounts/<int:pk>/deposit/",
        AccountDepositAPIView.as_view(),
        name="account-deposit"
    ),

    path(
        "accounts/<int:pk>/withdraw/",
        AccountWithdrawAPIView.as_view(),
        name="account-withdraw"
    ),


    # Transfers
    path(
        "transfers/",
        TransferAPIView.as_view(),
        name="transfer"
    ),


    # Cards
    path(
        "cards/",
        CardListCreateAPIView.as_view(),
        name="card-list-create"
    ),

    path(
        "cards/<int:pk>/",
        CardDetailAPIView.as_view(),
        name="card-detail"
    ),


    # Beneficiaries
    path(
        "beneficiaries/",
        BeneficiaryListCreateAPIView.as_view(),
        name="beneficiary-list-create"
    ),

    path(
        "beneficiaries/<int:pk>/",
        BeneficiaryDetailAPIView.as_view(),
        name="beneficiary-detail"
    ),
]