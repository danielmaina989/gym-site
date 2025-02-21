from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Affiliate(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="affiliate_profile")
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    commission_rate = models.FloatField(default=5.0)
    created_at = models.DateTimeField(auto_now_add=True)

    # New Fields for Bank Details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(
        max_length=20,
        choices=[("Bank Transfer", "Bank Transfer"), ("PayPal", "PayPal"), ("Other", "Other")],
        default="Bank Transfer",
    )

    def __str__(self):
        return f"Affiliate: {self.user.username} - {self.status}"

    def save(self, *args, **kwargs):
        """Generate a unique referral code before saving."""
        if not self.referral_code:  # Only generate if it's empty
            self.referral_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        """Generates a unique referral code."""
        while True:
            code = str(uuid.uuid4())[:8]  # Generate an 8-character unique code
            if not Affiliate.objects.filter(referral_code=code).exists():
                return code

    def update_earnings(self, amount):
        """Method to update the earnings for an affiliate."""
        self.total_earnings += amount
        self.save()




class Referral(models.Model):
    REFERRAL_STATUS = [
        ("Pending", "Pending"),
        ("Joined", "Joined"),
        ("Completed", "Completed"),
        ("Canceled", "Canceled"),
    ]

    referrer = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name="referrals")  # Changed to Affiliate
    referred_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="referred_by")
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referral_link = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=REFERRAL_STATUS, default="Pending")
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8]  # Generate unique code
        if not self.referral_link:
            self.referral_link = f"http://127.0.0.1:8000/register/?ref={self.referral_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.referrer.user.username} → {self.referred_user.username} ({self.status})"
