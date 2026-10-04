from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "Cần làm"
        DOING = "doing", "Đang làm"
        DONE = "done", "Hoàn thành"

    class Priority(models.TextChoices):
        LOW = "low", "Thấp"
        MEDIUM = "medium", "Trung bình"
        HIGH = "high", "Cao"

    title = models.CharField("Tên công việc", max_length=200)
    description = models.TextField("Mô tả", blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Người phụ trách",
                                 on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="assigned_tasks")
    department = models.ForeignKey("members.Department", verbose_name="Ban",
                                   on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="tasks")
    event = models.ForeignKey("events.Event", verbose_name="Sự kiện liên quan",
                              on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="tasks")
    status = models.CharField("Trạng thái", max_length=10, choices=Status.choices,
                              default=Status.TODO)
    priority = models.CharField("Ưu tiên", max_length=10, choices=Priority.choices,
                                default=Priority.MEDIUM)
    due_date = models.DateField("Hạn chót", null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, editable=False, related_name="created_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["due_date", "-created_at"]
        verbose_name = "Công việc"
        verbose_name_plural = "Công việc"

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return (self.due_date is not None and self.status != self.Status.DONE
                and self.due_date < timezone.localdate())

    def set_status(self, status):
        self.status = status
        self.completed_at = timezone.now() if status == self.Status.DONE else None
        self.save(update_fields=["status", "completed_at"])
