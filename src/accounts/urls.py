from django.contrib.auth.views import LoginView, PasswordResetView
from .views import UserRegisterView, ProfileDetailView
from .views import UserRegisterForm
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name='login'),
    path("reset/", PasswordResetView.as_view(template_name="registration/password_reset.html")),
    # path('register/', UserRegisterForm.as_view(), name='register'),
    path('registration/', UserRegisterView.as_view(), name='register'),
    path('account/', ProfileDetailView.as_view(), name='profile_detail'),
]
