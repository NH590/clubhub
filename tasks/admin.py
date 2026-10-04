from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assignee", "department", "status", "priority", "due_date")
    list_filter = ("status", "priority", "department")
    search_fields = ("title", "description")
    readonly_fields = ("created_by", "completed_at")
