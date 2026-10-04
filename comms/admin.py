from django.contrib import admin

from .models import Announcement, MeetingMinute


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "pinned", "ai_generated", "created_by", "created_at")
    list_filter = ("pinned", "ai_generated", "department")
    search_fields = ("title", "content")


@admin.register(MeetingMinute)
class MeetingMinuteAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location", "created_by")
    search_fields = ("title", "raw_notes", "summary")
    filter_horizontal = ("attendees",)
