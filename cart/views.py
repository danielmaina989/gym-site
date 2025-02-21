from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from shop.models import Product  # Import your Product model
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import json
from django.contrib import messages
from django.views import View
from django.db import transaction
from shop.models import Order
from affiliates.models import Referral
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from members.models import  Profile



@method_decorator(login_required, name='dispatch')
class CartDetailView(View):
    """Display the cart with session-stored items."""
    def get(self, request):
        cart = request.session.get("cart", {})  # Get cart session

        # print("🔹 Current Cart Session Data:", cart)  # Debugging output

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



class UpdateCartView(View):
    """Update quantity of a product in the cart."""
    
    def post(self, request, product_id):
        cart = request.session.get("cart", {})
        product = get_object_or_404(Product, id=product_id)

        try:
            data = json.loads(request.body)
            new_quantity = int(data.get("quantity", 1))

            if new_quantity < 1:
                return JsonResponse({"error": "Quantity must be at least 1"}, status=400)

            if str(product_id) in cart:
                cart[str(product_id)]["quantity"] = new_quantity
            else:
                return JsonResponse({"error": "Product not found in cart"}, status=400)

            # ✅ Recalculate Total Price
            total_price = 0
            for prod_id, item in cart.items():
                prod = Product.objects.get(id=int(prod_id))
                item["subtotal"] = float(prod.price) * item["quantity"]
                total_price += item["subtotal"]

            request.session["cart"] = cart
            request.session.modified = True

            return JsonResponse({
                "success": True,
                "subtotal": cart[str(product_id)]["subtotal"],
                "total": round(total_price, 2)
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


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


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        """Display checkout page with cart details."""
        cart = request.session.get("cart", {})
        total_price = sum(item["price"] * item["quantity"] for item in cart.values())

        return render(request, "checkout.html", {"cart": cart, "total_price": total_price})

    def post(self, request, *args, **kwargs):
        """Process checkout and apply referral commission."""
        cart = request.session.get("cart", {})

        if not cart:
            messages.error(request, "Your cart is empty!")
            return redirect("cart_summary")  # Redirect back to cart

        total_price = sum(item["price"] * item["quantity"] for item in cart.values())

        with transaction.atomic():  # Ensures atomic transaction
            # ✅ Create order
            order = Order.objects.create(user=request.user, total_price=total_price)

            # ✅ Apply referral commission (5% of total purchase)
            referral = Referral.objects.filter(referred_user=request.user, status="Joined").first()
            if referral:
                referrer = referral.referrer
                commission = total_price * 0.05

                # ✅ Assuming referrer has a profile with an earnings field
                referrer_profile = Profile.objects.get(user=referrer)
                referrer_profile.earnings += commission
                referrer_profile.save()

                referral.status = "Completed"
                referral.save()

            # ✅ Clear cart after checkout
            request.session["cart"] = {}

        messages.success(request, "Checkout successful! Your order has been placed.")
        return redirect("order_success")  # Redirect to success page
