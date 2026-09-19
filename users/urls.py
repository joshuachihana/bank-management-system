from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    BankTokenObtainPairView,
    CurrentUserView,
    CustomerViewSet,
    EmployeeViewSet,
    RoleViewSet,
    UserViewSet,
)


router = DefaultRouter()
router.register("roles", RoleViewSet, basename="role")
router.register("users", UserViewSet, basename="user")
router.register("customers", CustomerViewSet, basename="customer")
router.register("employees", EmployeeViewSet, basename="employee")


urlpatterns = [
    path("login/", BankTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", CurrentUserView.as_view(), name="current_user"),
] + router.urls
