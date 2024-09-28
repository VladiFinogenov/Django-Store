from decimal import Decimal
from django.core.cache import cache

import stripe
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, CreateView, View

from accounts.models import User
from order_ca.domain.entities.config import OrderStatus
from orders.models import Order
from shop.models import Cart, CartItem

stripe.api_key = settings.STRIPE_SECRET_KEY


@method_decorator(decorator=never_cache, name="get")
class PaymentProcess(View):

    def get(self, request, *args, **kwargs):
        # Здесь вы можете передать контекст, если нужно
        return redirect('shop:cart_detail')
        # return render(request, 'payments/payment_form.html')

    def post(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = cart.cart_items.all()

        # Удаление элементов
        if cart_items.exists():
            try:
                cart_items.delete()
                print("Cart items deleted successfully.")
            except Exception as e:
                print(f"Error deleting cart items: {e}")
        else:
            print("No items in cart to delete.")

        order_number = cache.get('order_number')

        order = get_object_or_404(Order, pk=order_number)
        order.order_status = OrderStatus.PAID.value

        order.save()

        if not order_number:
            return redirect('shop:cart_detail')

        return redirect('shop:cart_detail')


class PaymentCanceled(TemplateView):
    template_name = "payments/canceled.html"