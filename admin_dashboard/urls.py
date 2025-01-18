from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # your app views


app_name = 'admin_dashboard'
urlpatterns = [
    path('index/', views.HomeView.as_view(), name='index'),
    path('reviews/', views.ReviewListView.as_view(), name='review-list'),

]
