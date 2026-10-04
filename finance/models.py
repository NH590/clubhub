from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
    class Type(models.TextChoices):
        INCOME = "income", "Thu"
        EXPENSE = "expense", "Chi"

    name = models.CharField("Tên danh mục", max_length=100)
    type = models.CharField("Loại", max_length=10, choices=Type.choices)

    class Meta:
        ordering = ["type", "name"]
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    class Type(models.TextChoices):
        INCOME = "income", "Thu"
        EXPENSE = "expense", "Chi"

    class Status(models.TextChoices):
        PENDING = "pending", "Chờ duyệt"
        APPROVED = "approved", "Đã duyệt"
        REJECTED = "rejected", "Từ chối"

    type = models.CharField("Loại", max_length=10, choices=Type.choices)
    category = models.ForeignKey(Category, verbose_name="Danh mục",
                                 on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField("Số tiền (VNĐ)", max_digits=12, decimal_places=0,
                                 validators=[MinValueValidator(1)])
    description = models.CharField("Nội dung", max_length=255)
    date = models.DateField("Ngày", default=timezone.localdate)
    event = models.ForeignKey("events.Event", verbose_name="Sự kiện liên quan",
                              on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="transactions")
    receipt = models.FileField("Chứng từ", upload_to="receipts/", blank=True)
    status = models.CharField("Trạng thái", max_length=10, choices=Status.choices,
                              default=Status.PENDING, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, editable=False,
                                   related_name="transactions_created")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False,
                                    related_name="transactions_approved")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Khoản thu chi"
        verbose_name_plural = "Khoản thu chi"

    def __str__(self):
        return f"{self.get_type_display()} {self.amount:,.0f}đ - {self.description}"
