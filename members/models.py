from django.db import models

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
