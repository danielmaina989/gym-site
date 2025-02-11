from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path('', views.CartView.as_view(), name="cart_detail"),  # Example cart page
    path('add/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('remove/<int:product_id>/', views.remove_from_cart, name="remove_from_cart"),
]
