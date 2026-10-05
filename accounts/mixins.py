from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Chưa đăng nhập -> chuyển về trang login. Sai vai trò -> lỗi 403."""
    allowed_roles = ("admin", "board")

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role in self.allowed_roles