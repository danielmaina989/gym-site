from django.db import models
from gym.models import Service
from coaches.models import Coach
from django.contrib.auth.models import User
from django.utils.timezone import now 
from django.utils import timezone
from django.db import models



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.user.username}'s Profile"



# Create your models here.
class TrialUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Temporary fix
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
        default="Active",
    )

    def is_active(self):
        return self.trial_end_date >= now().date()


class Booking(models.Model):
    TIME_SLOT_CHOICES = [
        ('08:00', '08:00'),
        ('10:00', '10:00'),
        ('13:30', '13:30'),
        ('16:00', '16:00'),
        # Add more time slots as needed
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
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
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('canceled', 'Canceled')], default='active')
    
    def __str__(self):
        return f"Booking for {self.service.name} with {self.coach.name} on {self.session_date} at {self.training_time}"
    
from django.utils.timezone import now

class Membership(models.Model):
    MEMBERSHIP_CHOICES = [
        ('trial', 'Trial'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("expired", "Expired"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    membership_type = models.CharField(max_length=10, choices=MEMBERSHIP_CHOICES, default='trial')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    @property
    def is_active(self):
        """Check if the membership is still valid"""
        return self.end_date and self.end_date > now().date()
