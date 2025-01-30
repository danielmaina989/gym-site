from django.db import models
from gym.models import Service
from coaches.models import Coach
from django.contrib.auth.models import User
from django.utils.timezone import now


# Create your models here.
class TrialUser(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    trial_start_date = models.DateField(auto_now_add=True)
    trial_end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("Active", "Active"),
            ("Expired", "Expired"),
        ],
    )

    def __str__(self):
        return self.full_name


class Booking(models.Model):
    TIME_SLOT_CHOICES = [
        ('08:00', '08:00'),
        ('10:00', '10:00'),
        ('13:30', '13:30'),
        ('16:00', '16:00'),
        # Add more time slots as needed
    ]

    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    session_date = models.DateField()
    coach = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    training_time = models.CharField(
        max_length=5, 
        choices=TIME_SLOT_CHOICES, 
        default='08:00'  # Default to 08:00 (or another preferred time)
    )
    created_at = models.DateTimeField(default=now, editable=False)
    
    def __str__(self):
        return f"Booking for {self.service.name} with {self.coach.name} on {self.session_date} at {self.training_time}"