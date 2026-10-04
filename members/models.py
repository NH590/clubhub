from django.conf import settings
from django.db import models
from django.utils import timezone


class Department(models.Model):
    """Một ban trong CLB (Truyền thông, Sự kiện, Hậu cần...)."""

    name = models.CharField("Tên ban", max_length=100, unique=True)
    description = models.TextField("Mô tả", blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Trưởng ban",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="headed_departments",
    )
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Ban"
        verbose_name_plural = "Ban"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Membership(models.Model):
    """Một thành viên thuộc một ban."""

    class Position(models.TextChoices):
        HEAD = "head", "Trưởng ban"
        DEPUTY = "deputy", "Phó ban"
        MEMBER = "member", "Thành viên"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Thành viên",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    department = models.ForeignKey(
        Department,
        verbose_name="Ban",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    position = models.CharField(
        "Chức vụ", max_length=10, choices=Position.choices, default=Position.MEMBER
    )
    joined_at = models.DateField("Ngày tham gia", default=timezone.localdate)
    is_active = models.BooleanField("Còn hoạt động", default=True)

    class Meta:
        verbose_name = "Thành viên trong ban"
        verbose_name_plural = "Thành viên trong ban"
        ordering = ["department__name", "user__first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "department"], name="unique_user_department"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.department} ({self.get_position_display()})"