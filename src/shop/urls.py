from django.urls import path
from .views import ProductDetailView, ReviewCreateView, history_view


app_name = "shop"


urlpatterns = [
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path('product/<int:pk>/review/create/', ReviewCreateView.as_view(), name='review_create'),
    path('product/history/', history_view, name='product_history'),
    ]
