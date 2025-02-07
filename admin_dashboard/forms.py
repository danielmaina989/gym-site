# Admin View to Reply to an Enquiry
from django import forms
from gym.models import ContactSubmission

class EnquiryReplyForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['admin_reply']
        widgets = {
            'admin_reply': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }