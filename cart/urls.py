from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="cart_detail"),
    path("update/<int:product_id>/", views.UpdateCartView.as_view(), name="cart_update"),
    path("add/<int:product_id>/", views.AddToCartView.as_view(), name="cart_add"),
    path("remove/<int:product_id>/", views.RemoveFromCartView.as_view(), name="cart_remove"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("stripe/webhook/", views.StripeWebhookView.as_view(), name="stripe_webhook"),
    path("checkout/success/", views.OrderSuccessView.as_view(), name="order_success"),
    path("receipt/<int:order_id>/", views.download_receipt, name="download_receipt"),

]
