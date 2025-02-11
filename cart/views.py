from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse

class CartView(View):
    def get(self, request):
        return render(request, "cart/cart.html")  # Create this template later


def add_to_cart(request, product_id):
    # Temporary response to avoid errors
    return HttpResponse(f"Product {product_id} added to cart.")

def remove_from_cart(request, product_id):
    return HttpResponse(f"Product {product_id} removed from cart.")