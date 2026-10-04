from django.contrib import admin

from .models import Department, Membership


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "head", "created_at")
    search_fields = ("name",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "position", "joined_at", "is_active")
    list_filter = ("department", "position", "is_active")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__mssv",
    )