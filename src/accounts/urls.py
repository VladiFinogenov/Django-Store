from django.contrib.auth.views import LoginView, PasswordResetView
from django.urls import path
from .views import (
    PersonalAccountView,
    ProfileView,
    CustomRegistrationView,
    UserHistoryProductView,
    UserHistoryOrderView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("reset/", PasswordResetView.as_view(template_name="registration/password_reset.html")),
    path("registration/", CustomRegistrationView.as_view(template_name="registration/registration_form.html"),
         name="registration"),
    path("account/<int:pk>/", PersonalAccountView.as_view(template_name="accounts/account.html"), name="account"),
    path("profile/<int:pk>/", ProfileView.as_view(template_name="accounts/profile.html"), name="profile"),
    path("history/product/", UserHistoryProductView.as_view(), name="product_viewing_history"),
    path("history/order/", UserHistoryOrderView.as_view(), name="history_of_orders"),

]
