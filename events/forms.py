from django import forms

from .models import Event

DT_FORMAT = "%Y-%m-%dT%H:%M"


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "location", "start_time", "end_time",
                  "capacity", "department"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DT_FORMAT),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DT_FORMAT),
        }

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_time"), cleaned.get("end_time")
        if start and end and end <= start:
            self.add_error("end_time", "Thời gian kết thúc phải sau thời gian bắt đầu.")
        return cleaned