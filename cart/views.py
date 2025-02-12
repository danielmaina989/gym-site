from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from shop.models import Product  # Import your Product model
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView



@method_decorator(login_required, name='dispatch')


class CartDetailView(View):
    """Display the cart with session-stored items."""
    def get(self, request):
        cart = request.session.get("cart", {})  # Get cart session

        print("🔹 Current Cart Session Data:", cart)  # Debugging output

        cart_items = []
        total_price = 0

        for product_id, item in cart.items():
            try:
                product = get_object_or_404(Product, id=int(product_id))
                quantity = item["quantity"]
                subtotal = float(product.price) * quantity  # Convert Decimal to float

                total_price += subtotal

                cart_items.append({
                    "product": product,
                    "quantity": quantity,
                    "subtotal": subtotal,
                })
            except Exception as e:
                print(f"❌ Error fetching product {product_id}: {e}")

        return render(request, "cart/cart_detail.html", {
            "cart_items": cart_items,
            "total_price": total_price,
        })


@method_decorator(login_required, name='dispatch')


class AddToCartView(View):
    """Add a product to the cart session."""
    def post(self, request, product_id):
        cart = request.session.get("cart", {})

        try:
            product = Product.objects.get(id=product_id)
            product_id_str = str(product_id)  # Store keys as strings for JSON compatibility

            if product_id_str in cart:
                cart[product_id_str]["quantity"] += 1
            else:
                cart[product_id_str] = {
                    "quantity": 1,
                    "price": float(product.price)  # Convert Decimal to float
                }

            request.session["cart"] = cart
            request.session.modified = True  # Save session changes

            return JsonResponse({
                "message": f"{product.name} added to cart!",
                "cart_count": sum(item["quantity"] for item in cart.values()),
            })
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)


@method_decorator(login_required, name='dispatch')

class RemoveFromCartView(View):
    def post(self, request, product_id):
        cart = request.session.get("cart", {})

        print("Cart before removing:", cart)  # Debugging

        if not cart:
            return JsonResponse({"error": "Cart is empty"}, status=400)

        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session["cart"] = cart
            request.session.modified = True

            return JsonResponse({
                "message": "Product removed from cart",
                "cart_count": sum(item["quantity"] for item in cart.values())
            })

        return JsonResponse({"error": "Product not found in cart"}, status=400)


class CheckoutView(TemplateView):
    template_name = "cart/checkout.html"