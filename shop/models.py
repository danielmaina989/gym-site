# shop/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from decimal import Decimal
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    


class Affilliate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="affiliate_profile")
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Affiliate: {self.user.username}"

    def update_earnings(self, amount):
        """Method to update the earnings for an affiliate."""
        self.total_earnings += amount
        self.save()


class Refferral(models.Model):
    REFERRAL_STATUS = [
        ("Pending", "Pending"),
        ("Joined", "Joined"),
        ("Completed", "Completed"),
        ("Canceled", "Canceled"),
    ]

    referrer = models.ForeignKey(Affilliate, on_delete=models.CASCADE, related_name="referrals")  # Changed to Affiliate
    referred_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="referred_by")
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referral_link = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=REFERRAL_STATUS, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8]  # Generate unique code
        if not self.referral_link:
            self.referral_link = f"http://127.0.0.1:8000/register/?ref={self.referral_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.referrer.user.username} → {self.referred_user.username} ({self.status})"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    referrer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="referral_orders")
    commission_paid = models.BooleanField(default=False) 
    
    def __str__(self):
        return f"Order {self.id}"
    
    def calculate_commission(self):
        """Calculate the 5% commission for the referrer."""
        return self.total_amount * Decimal(0.05)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
