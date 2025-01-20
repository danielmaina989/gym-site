from django import forms
from .models import Review
from gym_blog.models import Post

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'comment']


