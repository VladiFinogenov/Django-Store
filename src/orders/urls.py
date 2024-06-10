from django.urls import path
from .views import (
    Step1UserData,
    Step2SelectDelivery,
    Step3SelectPayment,
    Step4OrderConfirmation
)

app_name = "orders"


urlpatterns = [
    path("create/", Step1UserData.as_view(), name='order_create'),
    path("select/delivery/", Step2SelectDelivery.as_view(), name='delivery'),
    path("select/payment/", Step3SelectPayment.as_view(), name='payment'),
    path("confirmation/", Step4OrderConfirmation.as_view(), name='confirmation'),
]
