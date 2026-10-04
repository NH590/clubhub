from django import forms

from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["type", "category", "amount", "date", "description", "event", "receipt"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def clean(self):
        cleaned = super().clean()
        t, cat = cleaned.get("type"), cleaned.get("category")
        if t and cat and cat.type != t:
            self.add_error("category", "Danh mục không khớp với loại Thu/Chi đã chọn.")
        return cleaned
