from django.contrib import admin

from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    list_filter = ("type",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "type", "category", "amount", "description", "status", "created_by")
    list_filter = ("type", "status", "category")
    search_fields = ("description",)
    readonly_fields = ("status", "created_by", "approved_by")
