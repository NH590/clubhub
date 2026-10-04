from django import forms

from events.models import Event
from members.models import Department

TONES = [
    ("thân thiện, trẻ trung", "Thân thiện, trẻ trung"),
    ("trang trọng, lịch sự", "Trang trọng"),
    ("hào hứng, truyền cảm hứng", "Hào hứng"),
    ("ngắn gọn, đi thẳng vào vấn đề", "Ngắn gọn"),
]


class DraftAnnouncementForm(forms.Form):
    event = forms.ModelChoiceField(label="Sự kiện (không bắt buộc)",
                                   queryset=Event.objects.order_by("-start_time"), required=False)
    key_points = forms.CharField(label="Ý chính cần truyền tải", required=False,
                                 widget=forms.Textarea(attrs={"rows": 4,
                                     "placeholder": "VD: miễn phí, có quà cho 20 bạn đầu tiên, nhớ mang laptop"}))
    tone = forms.ChoiceField(label="Giọng văn", choices=TONES)

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("event") and not cleaned.get("key_points"):
            raise forms.ValidationError("Hãy chọn sự kiện hoặc nhập ý chính.")
        return cleaned


class SuggestAssignmentForm(forms.Form):
    title = forms.CharField(label="Tên công việc", max_length=200)
    description = forms.CharField(label="Mô tả", required=False,
                                  widget=forms.Textarea(attrs={"rows": 3}))
    department = forms.ModelChoiceField(label="Ban liên quan", queryset=Department.objects.all(),
                                        required=False)
