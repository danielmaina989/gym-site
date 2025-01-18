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



