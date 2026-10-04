from django.conf import settings
from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    title = models.CharField("Tiêu đề", max_length=200)
    content = models.TextField("Nội dung")
    department = models.ForeignKey("members.Department", verbose_name="Gửi tới ban",
                                   on_delete=models.SET_NULL, null=True, blank=True,
                                   help_text="Để trống nếu gửi toàn CLB",
                                   related_name="announcements")
    event = models.ForeignKey("events.Event", verbose_name="Sự kiện liên quan",
                              on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="announcements")
    pinned = models.BooleanField("Ghim lên đầu", default=False)
    ai_generated = models.BooleanField("Viết nháp bằng AI", default=False, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, editable=False, related_name="announcements")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pinned", "-created_at"]
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"

    def __str__(self):
        return self.title


class MeetingMinute(models.Model):
    title = models.CharField("Tên cuộc họp", max_length=200)
    date = models.DateField("Ngày họp", default=timezone.localdate)
    location = models.CharField("Địa điểm", max_length=200, blank=True)
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name="Người tham dự",
                                       blank=True, related_name="meetings_attended")
    raw_notes = models.TextField("Ghi chép cuộc họp")
    summary = models.TextField("Tóm tắt", blank=True)
    ai_summarized_at = models.DateTimeField(null=True, blank=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, editable=False, related_name="minutes_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Biên bản họp"
        verbose_name_plural = "Biên bản họp"

    def __str__(self):
        return f"{self.title} ({self.date:%d/%m/%Y})"
