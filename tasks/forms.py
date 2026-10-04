from django import forms
from django.contrib.auth import get_user_model

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assignee", "department", "event",
                  "priority", "status", "due_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignee"].queryset = (
            get_user_model().objects.filter(is_active=True).order_by("first_name", "username")
        )

    def save(self, commit=True):
        task = super().save(commit=False)
        # Cập nhật thời điểm hoàn thành theo trạng thái chọn trong form
        if task.status == Task.Status.DONE and task.completed_at is None:
            from django.utils import timezone
            task.completed_at = timezone.now()
        elif task.status != Task.Status.DONE:
            task.completed_at = None
        if commit:
            task.save()
        return task
