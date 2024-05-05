from django.urls import path
from .views import (
    # ReviewListView,
    ProductDetailView,
    CommentCreateView,
)

app_name = "shop"


urlpatterns = [
    # path('product/', ProductDetailView.as_view(), name='products'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    # path('product/reviews/', ReviewListView.as_view(), name='review_list'),
    path('product/<int:pk>/review/create/', CommentCreateView.as_view(), name='review_create'),

    ]
