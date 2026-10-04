from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "mssv", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("username", "first_name", "last_name", "mssv", "email")
    fieldsets = UserAdmin.fieldsets + (
        ("Thông tin CLB", {"fields": ("role", "mssv", "phone", "faculty", "avatar")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Thông tin CLB", {"fields": ("role", "mssv", "email")}),
    )
