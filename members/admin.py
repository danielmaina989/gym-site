from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'user', 'session_date', 'training_time', 'created_at')  # Ensure these fields exist in the model
    list_filter = ('session_date', 'service')  # Add filters for session date and service
    search_fields = ('user__username', 'service__name')  # Enable search by user or service name
    ordering = ('-created_at',)  # Order bookings by creation date (newest first)

admin.site.register(Booking, BookingAdmin)
