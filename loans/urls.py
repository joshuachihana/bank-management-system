from django.urls import path

from .views import (
    LoanDecisionAPIView,
    LoanDetailAPIView,
    LoanListCreateAPIView,
    LoanPayAPIView,
    LoanPaymentDetailAPIView,
    LoanPaymentListAPIView,
)


urlpatterns = [

    # Loans
    path(
        "loans/",
        LoanListCreateAPIView.as_view(),
        name="loan-list-create",
    ),

    path(
        "loans/<int:pk>/",
        LoanDetailAPIView.as_view(),
        name="loan-detail",
    ),

    path(
        "loans/<int:pk>/decide/",
        LoanDecisionAPIView.as_view(),
        name="loan-decision",
    ),

    path(
        "loans/<int:pk>/pay/",
        LoanPayAPIView.as_view(),
        name="loan-pay",
    ),

    # Loan payments
    path(
        "loan-payments/",
        LoanPaymentListAPIView.as_view(),
        name="loan-payment-list",
    ),

    path(
        "loan-payments/<int:pk>/",
        LoanPaymentDetailAPIView.as_view(),
        name="loan-payment-detail",
    ),
]