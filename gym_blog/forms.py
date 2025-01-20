from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'image', 'category']  # Exclude 'pub_date' as it's auto-set

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can further customize the form here
