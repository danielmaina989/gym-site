from . import views
from django.urls import path

app_name = 'coaches'
urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
]