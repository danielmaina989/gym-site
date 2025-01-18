from django.contrib import admin
from .models import Review

# Customizing the admin interface for the Review model
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'comment', 'created_at')  # Fields to display in the list view
    search_fields = ('name', 'comment')  # Fields to search by in the admin interface
    list_filter = ('rating',)  # Filter options by rating

# Register the model with the custom admin class
admin.site.register(Review, ReviewAdmin)

