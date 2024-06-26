from django.urls import path
from django.urls import path
from shop.views import (
    history_view,
    ProductDetailView,
    ReviewCreateView,
    AddToCartView,
    CartDetailView,
    CartItemDeleteView,
    CartItemUpdateView,
)
app_name = "shop"


urlpatterns = [
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path('product/<int:pk>/review/create/', ReviewCreateView.as_view(), name='review_create'),
    path('product/history/', history_view, name='product_history'),
    path('cart/<int:pk>/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartDetailView.as_view(), name='cart_detail'),
    path('cart/item/<int:pk>/delete/', CartItemDeleteView.as_view(), name='cart_delete'),
    path('cart/item/<int:pk>/update/', CartItemUpdateView.as_view(), name='cart_update'),
]
