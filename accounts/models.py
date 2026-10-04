from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User tuy chinh: them MSSV, SDT, khoa, anh dai dien va vai tro."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Chủ nhiệm / Admin"
        BOARD = "board", "Ban điều hành"
        HEAD = "head", "Trưởng ban"
        MEMBER = "member", "Thành viên"

    role = models.CharField(
        "Vai trò", max_length=10, choices=Role.choices, default=Role.MEMBER
    )
    mssv = models.CharField("MSSV", max_length=20, blank=True)
    phone = models.CharField("Số điện thoại", max_length=15, blank=True)
    faculty = models.CharField("Khoa", max_length=100, blank=True)
    avatar = models.ImageField("Ảnh đại diện", upload_to="avatars/", blank=True)

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_board_or_above(self):
        return self.role in (self.Role.ADMIN, self.Role.BOARD)
