from django import forms

from .models import Department, Membership


class BootstrapDateMixin:
    """Đổi mọi ô ngày thành lịch chọn ngày của trình duyệt."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class DepartmentForm(BootstrapDateMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = "__all__"


class MembershipForm(BootstrapDateMixin, forms.ModelForm):
    class Meta:
        model = Membership
        fields = "__all__"