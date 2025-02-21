from django import forms
from .models import Affiliate

class AffiliateApplicationForm(forms.ModelForm):
    class Meta:
        model = Affiliate
        fields = ["bank_name", "account_number", "account_holder_name", "payment_method"]
        widgets = {
            "bank_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your bank name"}),
            "account_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter account number"}),
            "account_holder_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter account holder name"}),
            "payment_method": forms.Select(attrs={"class": "form-control"}),
        }
