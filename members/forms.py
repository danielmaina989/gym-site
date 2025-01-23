from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import TrialUser
from datetime import date, timedelta

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class TrialUserForm(forms.ModelForm):
    class Meta:
        model = TrialUser
        fields = ['full_name', 'email', 'phone_number']
    
    def save(self, commit=True):
        trial_user = super().save(commit=False)
        trial_user.trial_end_date = date.today() + timedelta(days=14)  # Automatically set the trial end date
        trial_user.status = "Active"  # Set default status as Active
        if commit:
            trial_user.save()
        return trial_user

