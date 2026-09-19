from django.contrib import admin

from .models import Customer, Employee, Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role", "status", "is_staff")
    list_filter = ("role", "status", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "national_id")
    search_fields = ("user__username", "user__first_name", "user__last_name", "national_id")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "branch", "position")
    list_filter = ("branch",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "position")
