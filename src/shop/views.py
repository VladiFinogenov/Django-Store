import random
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_page, cache_control
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from shop.models import Product, Review, SellerProduct, HistoryProduct
from shop.forms import ReviewForm
from django.core.cache.utils import make_template_fragment_key
from django.views.decorators.cache import never_cache
from django.contrib.sessions.backends import db
from django.db.models import Prefetch
from django.utils import timezone
from shop.mixins import NonCachingMixin
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.core.serializers import serialize, deserialize
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, CreateView, DeleteView, ListView, View, UpdateView
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpRequest, HttpResponseRedirect, HttpResponseBadRequest
from decimal import Decimal, InvalidOperation
from shop.utils import (
    add_to_session_cart,
    get_cart_from_session,
    get_total_price_from_session_cart,
    get_total_quantity_from_session_cart,
    remove_from_session_cart,
    update_session_cart,
)

from shop.models import (
    Product,
    Review,
    Seller,
    SellerProduct,
    Cart,
    CartItem,
)
from shop.forms import ReviewForm


@never_cache
def history_view(request: HttpRequest, limit=5) -> HttpResponse:
    """
    Представление для отображения истории просмотра товаров.
    """

    history_products = (
        HistoryProduct.history.all()[:limit]
    )

    return render(request, 'includes/history-product.html', {
        'recently_viewed_products': history_products
    })


def update_history_product(request, product_id):
    """
    Функция update_recently_viewed реализует логику добавление товара в список просмотренных.

    При добавлении нового товара, если этот товар есть в списке просмотренных,
    он со своего места перемещается в самое начало списка. То есть в этом списке
    не может быть двух одинаковых товаров. Если этот товар и есть уже на последнем месте,
    то ничего не происходит.
    """

    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        history_product, created = HistoryProduct.objects.get_or_create(user=request.user, product=product)
        if not created:
            history_product.created_at = timezone.now()
        history_product.save()


class ProductDetailView(NonCachingMixin, DetailView):
    template_name = 'shop/product.html'
    context_object_name = "product"
    model = Product

    def get_object(self, queryset=None):
        product_id = self.kwargs.get("pk")
        product_cache_key = f'product_cache_key:{product_id}'
        product_data = cache.get(product_cache_key)

        update_history_product(self.request, product_id)

        if product_data is None:
            product = get_object_or_404(Product, pk=product_id)
            product_data = serialize("json", [product])
            cache.set(product_cache_key, product_data, timeout=60 * 60 * 24)
        else:
            product = list(deserialize("json", product_data))[0].object

        return product

    def get_seller_products(self, product_id):
        seller_products_cache_key = f'seller_products_cache_key:{product_id}'
        seller_products_data = cache.get(seller_products_cache_key)

        if seller_products_data is None:
            seller_products = SellerProduct.objects.filter(product_id=product_id).prefetch_related("seller")
            seller_products_data = serialize("json", seller_products)
            cache.set(seller_products_cache_key, seller_products_data, timeout=60 * 60 * 24)
        else:
            seller_products = [obj.object for obj in deserialize("json", seller_products_data)]

        return seller_products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('pk')
        context['seller_products'] = seller_products_qs = self.get_seller_products(product_id)
        price = 0
        count = 0
        min_price = 0
        min_price_id = None
        for seller_product in seller_products_qs:
            price += seller_product.price
            count += 1
            if count == 1:
                min_price_id = seller_product.id
                min_price = price
            elif count > 1:
                if price < min_price:
                    min_price = price
                    min_price_id = seller_product.id

        if count > 0:
            context['average_price'] = Decimal(price) / count
            context['min_price_id'] = min_price_id
        else:
            context['average_price'] = Decimal(0)
            context['min_price_id'] = min_price_id
        context['product_min_price_id'] = seller_products_qs

        items_per_page = 3
        page_number = self.request.GET.get('page')
        paginator = Paginator(self.object.reviews.all(), items_per_page)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['form'] = ReviewForm()
        return context

# class ProductDetailView(NonCachingMixin, DetailView):
#
#     template_name = 'shop/product.html'
#     context_object_name = "product"
#     model = Product
#
#     def get_context_data(self, **kwargs):
#         context = super(ProductDetailView, self).get_context_data(**kwargs)
#         product_cache_key = f'product_{self.kwargs.get("pk")}'
#         product = cache.get(product_cache_key)
#
#         if product is None:
#             prefetch_reviews = Prefetch(
#                 lookup='reviews',
#                 queryset=Review.objects.select_related('author').all()
#             )
#
#             prefetch_sellers = Prefetch(
#                 lookup='seller_products',
#                 queryset=SellerProduct.objects.select_related('seller').all()
#             )
#
#             product = (Product.objects
#                        .prefetch_related(prefetch_reviews, prefetch_sellers, 'category')
#                        .get(pk=self.kwargs.get('pk')))
#
#             cache.set(product_cache_key, product, timeout=60 * 60 * 24)
#             update_history_product(self.request, product.id)
#
#         items_per_page = 3
#         page_number = self.request.GET.get('page')
#         paginator = Paginator(product.reviews.all(), items_per_page)
#         page_obj = paginator.get_page(page_number)
#
#         context['seller_products'] = product.seller_products.all()
#         context['page_obj'] = page_obj
#         context['form'] = ReviewForm()
#
#         return context


class ReviewCreateView(CreateView):
    """
    Представление: для создания отзыва к продукту.
    """

    model = Review
    form_class = ReviewForm

    def form_valid(self, form):
        cache.delete('product_cache_key')
        review = form.save(commit=False)
        review.product_id = self.kwargs.get('pk')
        review.author = self.request.user
        review.save()

        return redirect(review.product.get_absolute_url())

    # @cache_page(0)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            #login_url = reverse('login')
            message = f"<p>Необходимо авторизоваться для добавления комментариев</p>"\
                      "<a href='{login_url}'>авторизоваться</a>"
            messages.info(request, mark_safe(message))
            return redirect(reverse(
                viewname='shop:product_detail',
                kwargs={'pk': self.kwargs.get('pk')}
            ))
        else:
            return super(ReviewCreateView, self).dispatch(request, *args, **kwargs)


class CartDetailView(DetailView):
    model = Cart
    context_object_name = 'cart'
    template_name = 'shop/cart.html'

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            cart = Cart()
        return cart

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart = context['cart']
            context['cart_items'] = cart.cart_items.all().prefetch_related('product')
            context['total_price'] = cart.total_price()
            context['total_quantity'] = cart.total_quantity()
        else:
            context['cart_items'] = get_cart_from_session(self.request)
            context['total_price'] = get_total_price_from_session_cart(self.request)
            context['total_quantity'] = get_total_quantity_from_session_cart(self.request)
        return context


class AddToCartView(View):
    """
    Представление: добавление товара в корзину
    """

    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        product = get_object_or_404(SellerProduct, id=product_id)
        quantity = request.POST.get('amount', '1')
        if not quantity.isdigit():
            return HttpResponseBadRequest("Количество должно быть числом.")
        quantity = int(quantity)
        if quantity <= 0:
            return HttpResponseBadRequest("Количество должно быть больше нуля.")

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.add_product(product, quantity=quantity)
        else:
            add_to_session_cart(request, product_id, quantity)

        return redirect('shop:product_detail', product.product.id)


class CartItemDeleteView(View):
    """
    Представление: удвление товара из корзины
    """

    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item = get_object_or_404(CartItem, id=product_id)
            cart.delete_product(cart_item)
        else:
            remove_from_session_cart(self.request, product_id)

        return redirect('shop:cart_detail')


class CartItemUpdateView(View):
    """
    Представление: изменение количества товара в корзине
    """

    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        quantity = request.POST.get('amount')
        if not quantity.isdigit():
            return HttpResponseBadRequest("Количество должно быть числом.")
        quantity = int(quantity)
        if quantity < 0:
            return HttpResponseBadRequest("Количество должно быть не меньше нуля.")

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            product = get_object_or_404(CartItem, id=product_id)
            cart.update_product(product, quantity=quantity)
        else:
            update_session_cart(request, product_id, quantity)

        return redirect('shop:cart_detail')
