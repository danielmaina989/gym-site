from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import TrialUser, Booking
from datetime import date, timedelta
from gym.models import Service
from coaches.models import Coach
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from affiliates.models import Referral, Affiliate

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    referral_code = forms.CharField(
        max_length=20,
        required=False,  # Referral code is optional
        widget=forms.TextInput(attrs={'placeholder': 'Referral Code (Optional)'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'referral_code']

    def clean_referral_code(self):
        """Validate referral code if provided."""
        referral_code = self.cleaned_data.get("referral_code")

        if referral_code:
            # ✅ Check if an active affiliate owns this code
            if not Affiliate.objects.filter(referral_code=referral_code, status="Active").exists():
                raise forms.ValidationError("Invalid or inactive referral code.")

        return referral_code


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()

            # ✅ Handle referral logic if referral code exists
            referral_code = self.cleaned_data.get("referral_code")
            if referral_code:
                try:
                    referral = Referral.objects.get(referral_code=referral_code, status="Pending")
                    referral.referred_user = user
                    referral.status = "Joined"
                    referral.save()
                except Referral.DoesNotExist:
                    pass  # Ignore if referral doesn't exist (shouldn't happen due to validation)

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



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'session_date', 'training_time', 'coach']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'session_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'training_time': forms.Select(attrs={'class': 'form-control'}),  # Ensure it's included here
            'coach': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure training_time choices are set
        self.fields['training_time'].choices = Booking.TIME_SLOT_CHOICES

        # Customize coach display format
        self.fields['coach'].queryset = Coach.objects.all()
        self.fields['coach'].label_from_instance = lambda coach: f"{coach.name} - {coach.specialization}"
