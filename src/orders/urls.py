from django.urls import path
from .views import (
    Step1UserData,
    Step2SelectDelivery,
    Step3SelectPayment,
    Step4OrderConfirmation,
    OrderDetail,
)

app_name = "orders"

urlpatterns = [
    path("create/", Step1UserData.as_view(), name='order_create'),
    path("select/delivery/", Step2SelectDelivery.as_view(), name='select_delivery'),
    path("select/payment/", Step3SelectPayment.as_view(), name='select_payment'),
    path("confirmation/", Step4OrderConfirmation.as_view(), name='confirmation'),
    path("order/<int:pk>/", OrderDetail.as_view(), name='order_detail'),
]
