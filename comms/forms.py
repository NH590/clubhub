from django import forms
from django.contrib.auth import get_user_model

from .models import Announcement, MeetingMinute


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "content", "department", "event", "pinned"]
        widgets = {"content": forms.Textarea(attrs={"rows": 10})}


class MeetingMinuteForm(forms.ModelForm):
    class Meta:
        model = MeetingMinute
        fields = ["title", "date", "location", "attendees", "raw_notes", "summary"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "attendees": forms.CheckboxSelectMultiple,
            "raw_notes": forms.Textarea(attrs={"rows": 10,
                                               "placeholder": "Ghi lại nội dung cuộc họp, ý kiến, quyết định..."}),
            "summary": forms.Textarea(attrs={"rows": 6,
                                             "placeholder": "Có thể để trống rồi bấm 'Tóm tắt bằng AI' sau khi lưu"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attendees"].queryset = (
            get_user_model().objects.filter(is_active=True).order_by("first_name", "username")
        )
