from django.shortcuts import render
from django.views.generic import ListView,TemplateView
from gym.models import Review
from django.urls import path
from django.contrib import admin
from django.shortcuts import redirect


class HomeView(TemplateView):
    template_name = "admin_dashboard/index.html"

class ReviewListView(ListView):
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'

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
    extra_context["title"] = "Trial User Analytics"
    return super().changelist_view(request, extra_context=extra_context)


