from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserRegisterForm, UserLoginForm
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DetailView, CreateView, ListView, View
from orders.models import Order
from .models import User
from shop.models import HistoryProduct
from django.contrib.auth.mixins import LoginRequiredMixin
from django_registration.backends.activation.views import RegistrationView
from .forms import UserRegisterForm, UserUpdateForm


class UserLoginView(SuccessMessageMixin, LoginView):
    """
    Авторизация на сайте
    """

    form_class = UserLoginForm
    template_name = 'registration/login.html'
    next_page = 'home'
    success_message = 'Добро пожаловать на сайт!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация на сайте'
        return context

    def form_valid(self, form):
        form_result = super().form_valid(form)
        user = form.get_user()
        user.save()
        return form_result


class UserRegisterView(SuccessMessageMixin, CreateView):
    """
    Представление регистрации на сайте с формой регистрации
    """

    form_class = UserRegisterForm
    success_url = reverse_lazy('home')
    template_name = 'registration/registration_form.html'
    success_message = 'Вы успешно зарегистрировались. Можете войти на сайт!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация на сайте'
        return context


class CustomRegistrationView(RegistrationView):
    form_class = UserRegisterForm
    template_name = 'registration/registration_form.html'

    def get_success_url(self, user=None):
        return reverse_lazy("accounts:login")


class PersonalAccountView(LoginRequiredMixin, DetailView):
    """
    Свободная страница личного кабинета, на которой отображаются данные о пользователе:
    """
    template_name = 'accounts/account.html'
    success_url = reverse_lazy("accounts:account")
    model = User
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        order = Order.objects.filter(user=user).order_by('-created_at').first()
        context['order'] = order
        return context


class ProfileView(UpdateView):
    model = User
    template_name = 'accounts/profile.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy("accounts:profile")
    context_object_name = 'user'

    def get_success_url(self):
        return reverse_lazy('accounts:account', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class UserHistoryProductView(View):
    """
    Представление для отображения списка просмотренных товаров.
    """

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = request.user.pk
        history = HistoryProduct.objects.filter(user=user)[:8]
        return render(request, template_name="accounts/history-product.html",
                      context={"recently_viewed_products": history})


class UserHistoryOrderView(ListView):
    """
    Представление для отображения списка заказов пользователя.
    """

    template_name = 'accounts/history-order.html'
    model = Order
    context_object_name = 'orders'

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(user=user).order_by('-created_at')
        return queryset
