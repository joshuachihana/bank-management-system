from rest_framework.permissions import SAFE_METHODS, BasePermission


STAFF_ROLES = {"Admin", "Manager", "Teller", "Auditor", "System"}
OPERATIONS_ROLES = {"Admin", "Manager", "Teller"}
MANAGEMENT_ROLES = {"Admin", "Manager"}


def user_role(user):
    if not user or not user.is_authenticated:
        return None
    role = getattr(user, "role", None)
    return getattr(role, "name", None)


def is_customer(user):
    return user_role(user) == "Customer"


def is_staff_role(user):
    return user_role(user) in STAFF_ROLES


def is_operations_role(user):
    return user_role(user) in OPERATIONS_ROLES


def is_management_role(user):
    return user_role(user) in MANAGEMENT_ROLES


class IsActiveAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.status == "ACTIVE"
        )


class IsBankStaff(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.status == "ACTIVE"
            and is_staff_role(request.user)
        )


class IsOperationsStaff(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.status == "ACTIVE"
            and is_operations_role(request.user)
        )


class IsManagementStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and request.user.status == "ACTIVE"
            and is_management_role(request.user)
        )
