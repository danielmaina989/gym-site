from django.contrib import admin
from .models import Review, Service, ContactSubmission

# Customizing the admin interface for the Review model
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'comment', 'created_at')  # Fields to display in the list view
    search_fields = ('name', 'comment')  # Fields to search by in the admin interface
    list_filter = ('rating',)  # Filter options by rating


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_session', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')

# Register the model with the custom admin class
admin.site.register(Review, ReviewAdmin)


@admin.register(ContactSubmission)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'enquiry_type', 'submitted_at') 
    search_fields = ('name', 'email', 'message')
    list_filter = ('enquiry_type', 'submitted_at')
    ordering = ('-submitted_at',)

