from django.contrib import admin
from .models import Booking, Membership
from django.utils import timezone
from django.utils.html import format_html

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'user', 'session_date', 'training_time', 'created_at')  # Ensure these fields exist in the model
    list_filter = ('session_date', 'service')  # Add filters for session date and service
    search_fields = ('user__username', 'service__name')  # Enable search by user or service name
    ordering = ('-created_at',)  # Order bookings by creation date (newest first)

admin.site.register(Booking, BookingAdmin)


class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "membership_type", "is_active_status")

    @admin.display(boolean=True)  # ✅ This tells Django it's a boolean field
    def is_active_status(self, obj):
        return obj.status == "active"

admin.site.register(Membership, MembershipAdmin)

