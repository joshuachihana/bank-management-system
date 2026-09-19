from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Customer, Employee, Role
from .permissions import IsBankStaff, IsManagementStaffOrReadOnly, is_customer
from .serializers import (
    BankTokenObtainPairSerializer,
    CustomerSerializer,
    EmployeeSerializer,
    RoleSerializer,
    UserSerializer,
    UserWriteSerializer,
)
from .services import write_audit_log


class BankTokenObtainPairView(TokenObtainPairView):
    serializer_class = BankTokenObtainPairSerializer


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsManagementStaffOrReadOnly]


class UserViewSet(ModelViewSet):
    queryset = UserSerializer.Meta.model.objects.select_related("role")
    permission_classes = [IsManagementStaffOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH"):
            return UserWriteSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_customer(self.request.user):
            return queryset.filter(pk=self.request.user.pk)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        write_audit_log(self.request, "CREATE", "users", instance.pk, "Created user.")

    def perform_update(self, serializer):
        instance = serializer.save()
        write_audit_log(self.request, "UPDATE", "users", instance.pk, "Updated user.")


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related("user", "user__role")
    serializer_class = CustomerSerializer
    permission_classes = [IsManagementStaffOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_customer(self.request.user):
            return queryset.filter(user=self.request.user)
        return queryset


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.select_related("user", "user__role", "branch")
    serializer_class = EmployeeSerializer
    permission_classes = [IsBankStaff]
