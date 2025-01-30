# coaches/admin.py
from django.contrib import admin
from .models import Coach


# coaches/admin.py
@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'experience', 'email')
    search_fields = ('name', 'specialization')
    list_filter = ('experience',)
    fields = ('name', 'specialization', 'experience', 'email', 'phone', 'photo', 'workout_video')
