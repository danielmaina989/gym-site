from django.db import models

# Create your models here.

class Review(models.Model):
    name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating}"


class Service(models.Model):
    # Define predefined categories for services
    YOGA = 'Yoga'
    CROSSFIT = 'CrossFit'
    PERSONAL_TRAINER = 'Personal Trainer'
    NUTRITIONIST = 'Nutritionist'

    SERVICE_CATEGORIES = [
        (YOGA, 'Yoga'),
        (CROSSFIT, 'CrossFit'),
        (PERSONAL_TRAINER, 'Personal Trainer'),
        (NUTRITIONIST, 'Nutritionist'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/')
    price_per_session = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Adding category choices to the service
    category = models.CharField(
        max_length=50,
        choices=SERVICE_CATEGORIES,
        default=YOGA,
    )

    def __str__(self):
        return self.name


from django.db import models
from django.utils.timezone import now

class ContactSubmission(models.Model):
    ENQUIRY_TYPE_CHOICES = [
        ('enquiry', 'Enquiry'),
        ('complaint', 'Complaint'),
        ('pricing', 'Pricing'),
        ('membership', 'Membership'),
        ('other', 'Other'),
        ('feedback', 'Feedback'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    enquiry_type = models.CharField(max_length=20, choices=ENQUIRY_TYPE_CHOICES, default='enquiry')
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Admin reply fields
    admin_reply = models.TextField(blank=True, null=True)
    is_replied = models.BooleanField(default=False)
    responded_at = models.DateTimeField(blank=True, null=True)
    
    # Follow-up fields
    follow_up = models.TextField(blank=True, null=True)
    follow_up_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.enquiry_type})"
