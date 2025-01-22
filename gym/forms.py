from django import forms
from .models import Review, ContactSubmission
from gym_blog.models import Post

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'comment']


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'message', 'enquiry_type']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

