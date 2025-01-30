from django import forms
from .models import Review, ContactSubmission, Service
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

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'image', 'price_per_session', 'is_active', 'category']