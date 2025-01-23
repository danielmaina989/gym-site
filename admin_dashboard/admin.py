from django.contrib import admin
from django.db import models
# Register your models here.
from django.contrib import admin
from django.db.models import Count
from members.models import TrialUser

@admin.register(TrialUser)
class TrialUserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "trial_start_date", "trial_end_date", "status")
    list_filter = ("status", "trial_start_date")

    def changelist_view(self, request, extra_context=None):
        # Aggregate data for analytics
        data = TrialUser.objects.aggregate(
            total_signups=Count("id"),
            active_trials=Count("id", filter=models.Q(status="Active")),
            expired_trials=Count("id", filter=models.Q(status="Expired")),
        )

        # Add aggregated data to the context
        extra_context = extra_context or {}
        extra_context["analytics"] = data
        return super().changelist_view(request, extra_context=extra_context)
