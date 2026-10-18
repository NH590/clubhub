from django import forms
from django.contrib.auth import get_user_model


class ProfileForm(forms.ModelForm):
    """Thành viên tự sửa thông tin cá nhân (không sửa MSSV, vai trò, ban)."""

    class Meta:
        model = get_user_model()
        fields = ["last_name", "first_name", "email", "phone", "faculty", "avatar"]
        labels = {
            "last_name": "Họ và tên đệm",
            "first_name": "Tên",
            "email": "Email",
            "phone": "Số điện thoại",
            "faculty": "Khoa",
            "avatar": "Ảnh đại diện",
        }
