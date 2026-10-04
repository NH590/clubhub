from django.contrib import admin

from .models import Event, Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ("registered_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "start_time", "department", "capacity")
    list_filter = ("department",)
    search_fields = ("title", "location")
    readonly_fields = ("created_by", "checkin_token")
    inlines = [RegistrationInline]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "registered_at", "checked_in_at")
    list_filter = ("event",)