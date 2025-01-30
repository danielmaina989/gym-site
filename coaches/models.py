# coaches/models.py
from django.db import models

class Coach(models.Model):
    CATEGORY_CHOICES = [
        ('Personal Trainer', 'Personal Trainer'),
        ('Yoga Instructor', 'Yoga Instructor'),
        ('Nutritionist', 'Nutritionist'),
        ('Strength Coach', 'Strength Coach'),
    ]
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='coaches_photos/', null=True, blank=True)
    workout_video = models.FileField(upload_to='coaches_videos/', null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    resume = models.FileField(upload_to='nutritionist_resumes/', null=True, blank=True, help_text="Required for Nutritionists")

    def __str__(self):
        return self.name
