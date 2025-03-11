# shop/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from decimal import Decimal
from affiliates.models import Referral

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
    


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    referral = models.ForeignKey(Referral, on_delete=models.SET_NULL, null=True, blank=True)
    commission_paid = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

    
    def __str__(self):
        return f"Order {self.id}"
    
    def calculate_commission(self):
        """Calculate the 5% commission for the referrer."""
        return self.total_amount * Decimal(0.05)

    def save(self, *args, **kwargs):
        """Automatically update affiliate earnings when order is paid."""
        
        # Check if the order is now paid, and commission hasn't been paid yet
        is_paid_now = self.paid and not Order.objects.filter(pk=self.pk, paid=True).exists()

        if is_paid_now and self.referral and not self.commission_paid:
            affiliate = self.referral.referrer  # Get the affiliate who referred the buyer
            commission = self.calculate_commission()  # Calculate 5% commission
            
            if affiliate:
                affiliate.update_earnings(commission)  # ✅ Add commission to affiliate
                self.commission_paid = True  # ✅ Mark commission as paid
        
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
