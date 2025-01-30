# coaches/forms.py
from django import forms
from .models import Coach
from members.models import Booking

class CoachForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = ['name', 'specialization', 'experience', 'email', 'phone', 'photo', 'workout_video', 'hourly_rate', 'resume']

    def clean(self):
        cleaned_data = super().clean()
        specialization = cleaned_data.get('specialization')
        resume = cleaned_data.get('resume')

        if specialization == 'Nutritionist' and not resume:
            raise forms.ValidationError("A resume is required for Nutritionists.")
        return cleaned_data
        


from django import forms
from django.core.exceptions import ValidationError
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from members.models import Booking, Coach

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'session_date', 'training_time', 'coach']  # ✅ Added 'training_time'

    coach = forms.ModelChoiceField(
        queryset=Coach.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Choose Coach"
    )

    session_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Preferred Date"
    )

    training_time = forms.ChoiceField(  # ✅ Explicitly define training_time field
        choices=[],  # Set dynamically in __init__
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Training Time"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Debugging: Print available fields
        print("Available form fields:", self.fields.keys())

        # Ensure training_time exists before setting choices
        if 'training_time' in self.fields:
            self.fields['training_time'].choices = Booking.TIME_SLOT_CHOICES  # ✅ Now it won't raise KeyError

        # Update the label of each coach with specialization
        self.fields['coach'].queryset = Coach.objects.all()
        for coach in self.fields['coach'].queryset:
            coach.name = f"{coach.name} - {coach.specialization}"  # Modify the name field to include specialization

    def clean_session_date(self):
        # Get the date from the form
        session_date = self.cleaned_data.get('session_date')

        # Check if the session date is in the past
        if session_date < date.today():
            raise ValidationError("The session date cannot be in the past. Please choose a future date.")

        return session_date
