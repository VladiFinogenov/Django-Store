from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category, Product, SellerProduct, Cart, CartItem
from django.contrib.auth.signals import user_logged_in
from shop.utils import get_cart_from_session, clear_session_cart


@receiver(signal=post_save, sender=Category)
@receiver(signal=post_delete, sender=Category)
def clear_menu_cache(sender, **kwargs):
    cache.delete('categories')


@receiver(post_save, sender=Product)
def reset_cache(sender, instance, **kwargs):
    cache.delete('product_cache_key')


@receiver(post_save, sender=SellerProduct)
@receiver(post_delete, sender=SellerProduct)
def clear_product_cache(sender, **kwargs):
    cache.delete('products')


@receiver(user_logged_in)
def merge_carts(sender, user, request, **kwargs):
    session_cart = get_cart_from_session(request)

    user_cart, created = Cart.objects.get_or_create(user=user)

    for item in session_cart:
        user_cart.add_product(item.product, item.quantity)
    clear_session_cart(request)
