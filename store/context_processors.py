from .models import Cart, Wishlist


def cart_count(request):
    count = 0
    wishlist_count = 0
    wishlist_product_ids = []

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            count = cart.total_items

        wishlist_qs = Wishlist.objects.filter(user=request.user)
        wishlist_count = wishlist_qs.count()
        wishlist_product_ids = list(
            wishlist_qs.values_list('product_id', flat=True)
        )

    return {
        'cart_count': count,
        'wishlist_count': wishlist_count,
        'wishlist_product_ids': wishlist_product_ids,
    }