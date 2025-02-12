from .models import CartItem

def cart_count(request):
    count = 0

    if request.user.is_authenticated:
        count = CartItem.objects.filter(cart__user=request.user).count()
    else:
        cart = request.session.get("cart", {})
        count = sum(item["quantity"] for item in cart.values())

    return {"cart_count": count}
