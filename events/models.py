import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

CHECKIN_EARLY_MINUTES = 30  # mở điểm danh trước giờ bắt đầu 30 phút


class Event(models.Model):
    title = models.CharField("Tên sự kiện", max_length=200)
    description = models.TextField("Mô tả", blank=True)
    location = models.CharField("Địa điểm", max_length=200)
    start_time = models.DateTimeField("Bắt đầu")
    end_time = models.DateTimeField("Kết thúc")
    capacity = models.PositiveIntegerField(
        "Số lượng tối đa", null=True, blank=True, help_text="Để trống nếu không giới hạn"
    )
    department = models.ForeignKey(
        "members.Department", verbose_name="Ban phụ trách",
        on_delete=models.SET_NULL, null=True, blank=True, related_name="events",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, editable=False, related_name="created_events",
    )
    checkin_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_time"]
        verbose_name = "Sự kiện"
        verbose_name_plural = "Sự kiện"

    def __str__(self):
        return self.title

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return "upcoming"
        if now <= self.end_time:
            return "ongoing"
        return "past"

    @property
    def registered_count(self):
        return self.registrations.count()

    @property
    def checked_in_count(self):
        return self.registrations.filter(checked_in_at__isnull=False).count()

    @property
    def is_full(self):
        return self.capacity is not None and self.registered_count >= self.capacity

    @property
    def checkin_open(self):
        now = timezone.now()
        return self.start_time - timedelta(minutes=CHECKIN_EARLY_MINUTES) <= now <= self.end_time

    def regenerate_token(self):
        self.checkin_token = uuid.uuid4()
        self.save(update_fields=["checkin_token"])


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              related_name="registrations", verbose_name="Sự kiện")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="event_registrations", verbose_name="Thành viên")
    registered_at = models.DateTimeField("Đăng ký lúc", auto_now_add=True)
    checked_in_at = models.DateTimeField("Điểm danh lúc", null=True, blank=True)

    class Meta:
        ordering = ["registered_at"]
        verbose_name = "Đăng ký sự kiện"
        verbose_name_plural = "Đăng ký sự kiện"
        constraints = [
            models.UniqueConstraint(fields=["event", "user"], name="unique_event_user"),
        ]

    def __str__(self):
        return f"{self.user} - {self.event}"