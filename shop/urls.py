from . import views
from django.urls import path

app_name = 'shop'
urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
]