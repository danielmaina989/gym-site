from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from shop.models import Product
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import json
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from django.db import transaction
from shop.models import Order
from affiliates.models import Referral
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from members.models import  Profile
import stripe
import logging
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db import transaction

stripe.api_key = settings.STRIPE_SECRET_KEY  # Ensure this is set in settings.py

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
                    "name": product.name,  # ✅ Add product name
                    "quantity": 1,
                    "price": float(product.price),  # Convert Decimal to float
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


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        """Display checkout page with cart details."""
        cart = request.session.get("cart", {})
        if not cart:
            messages.error(request, "Your cart is empty!")
            return redirect("cart_summary")

        total_price = sum(item["price"] * item["quantity"] for item in cart.values())
        return render(request, "cart/checkout.html", {"cart": cart, "total_price": total_price})

    def post(self, request, *args, **kwargs):
        cart = request.session.get("cart", {})
        if not cart:
            messages.error(request, "Your cart is empty!")
            return redirect("cart_summary")

        total_price = sum(item["price"] * item["quantity"] for item in cart.values())

        # ✅ Create an unpaid order (But don't save it yet)
        order = Order.objects.create(user=request.user, paid=False)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": item["name"]},
                        "unit_amount": int(item["price"] * 100),
                    },
                    "quantity": item["quantity"],
                }
                for item in cart.values()
            ],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("cart:order_success")) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("cart:cart_detail")),
            metadata={"user_id": request.user.id, "order_id": order.id},  # ✅ Store order_id in metadata
        )
        # ✅ Save session_id to the order
        order.stripe_session_id = checkout_session.id
        order.save()

        return redirect(checkout_session.url)


logger = logging.getLogger(__name__)
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.headers.get("Stripe-Signature")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except stripe.error.SignatureVerificationError:
            logger.error("🚨 Stripe signature verification failed!")
            return JsonResponse({"error": "Invalid signature"}, status=400)

        logger.info("🔄 Stripe Webhook Triggered!")

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            stripe_session_id = session.get("id")

            # ✅ Log full session data for debugging
            logger.info(f"🔹 Stripe Session Data: {session}")

            # ✅ Check if metadata exists
            metadata = session.get("metadata")
            if not metadata:
                logger.error("🚨 No metadata found in Stripe session!")
                return JsonResponse({"error": "Missing metadata"}, status=400)

            user_id = metadata.get("user_id")
            order_id = metadata.get("order_id")

            logger.info(f"🔹 Processing payment for user_id={user_id}, order_id={order_id}, session_id={stripe_session_id}")

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f"🚨 User with id {user_id} not found!")
                return JsonResponse({"error": "User not found"}, status=400)

            with transaction.atomic():
                # ✅ First, find the order by session ID (to handle Stripe retries)
                order = Order.objects.filter(stripe_session_id=stripe_session_id).first()

                # ✅ If not found, try finding it by order ID
                if not order:
                    order = Order.objects.filter(id=order_id).first()

                if order:
                    logger.info(f"✅ Found Order {order.id} (Paid={order.paid}), updating to Paid=True")

                    # ✅ Update order status
                    order.paid = True
                    order.stripe_session_id = stripe_session_id  # Store the latest session ID
                    order.save()

                    # ✅ Fetch again to confirm update
                    order.refresh_from_db()
                    logger.info(f"✅ Order {order.id} updated! Paid={order.paid}")

                else:
                    logger.warning(f"⚠️ No matching order found, creating a new one!")

                    # ✅ Create a new order only if none exist
                    order = Order.objects.create(
                        user=user,
                        paid=True,
                        stripe_session_id=stripe_session_id,
                    )

                    logger.info(f"✅ New Order {order.id} created with stripe_session_id: {order.stripe_session_id}")

        return JsonResponse({"status": "success"}, status=200)


logger = logging.getLogger(__name__)
class OrderSuccessView(TemplateView):
    template_name = "cart/order_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        session_id = self.request.GET.get("session_id")
        if session_id:
            order = Order.objects.filter(stripe_session_id=session_id, paid=True).first()
        else:
            order = Order.objects.filter(user=self.request.user, paid=True).last()

        if not order:
            logger.warning(f"🚨 No order found for session_id={session_id}")

            orders = Order.objects.filter(paid=True).values("id", "stripe_session_id")
            logger.warning(f"🔍 Found orders: {list(orders)}")
        
        context["order_id"] = order.id if order else None
        return context


def download_receipt(request, order_id):
    """Generate and download the order receipt as a PDF."""
    order = Order.objects.get(id=order_id)

    # Context for the template
    context = {
        "order": order,
        "user": order.user,
        "total_price": order.calculate_commission(),  # Assuming there's a total amount calculation method
    }

    # Render receipt template as an HTML string
    html_string = render_to_string("download_receipt.html", context)

    # Create a temporary PDF file
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="receipt_{order.id}.pdf"'

    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        HTML(string=html_string).write_pdf(temp_file.name)
        with open(temp_file.name, "rb") as pdf_file:
            response.write(pdf_file.read())

    return response
