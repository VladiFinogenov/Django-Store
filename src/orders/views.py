from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.views.generic import FormView, TemplateView
from django.urls import reverse, reverse_lazy
from .models import Order
from accounts.models import User
from .forms import (
    UserDataForm,
    PasswordForm,
    SelectDeliveryForm,
    SelectPaymentForm
)


class Step1UserData(FormView):
    """
    Шаг 1. Оформление заказа.
    Для авторизованного пользователя данные из профиля подставляются из базы данных.
    Для не авторизованного пользователя можно ввести данные с паролем в форму и попробовать
    зарегистрироваться, после чего продолжить оформление заказа.
    После успешной валидации данных идет перенаправление на следующий шаг (выбор доставки).
    """

    template_name = 'orders/step1-user-data.html'
    form_class = UserDataForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            context['password_form'] = PasswordForm()
        context['current_step'] = 'step1'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        if user.is_authenticated:
            kwargs['initial'] = {
                'full_name': user.get_full_name,
                'phone': user.phone,
                'email': user.email,
            }
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            success_url = reverse('orders:delivery')
            return redirect(success_url)
        else:
            password = form.cleaned_data.get('password2')
            email = form.cleaned_data.get('email')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            middle_name = form.cleaned_data.get('middle_name')
            phone = form.cleaned_data.get('phone')

            # Создание нового пользователя с введенным данными из формы.
            user = User.objects.create_user(
                last_name=last_name,
                username=username,
                middle_name=middle_name,
                email=email,
                password=password,
                phone=phone
            )
            login(self.request, user)
            success_url = reverse('orders:delivery')
            return redirect(success_url)


class Step2SelectDelivery(FormView):
    template_name = 'orders/step2-select-delivery.html'
    form_class = SelectDeliveryForm
    success_url = reverse_lazy('orders:payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_step'] = 'step2'
        return context

    def form_valid(self, form):
        delivery_method = form.cleaned_data['delivery_method']
        city = form.cleaned_data['city']
        address = form.cleaned_data['address']
        order_data = cache.get('order_data', {})
        order_data.update({
            'delivery_method': delivery_method,
            'city': city,
            'address': address,
        })
        cache.set('order_data', order_data)

        return super().form_valid(form)


class Step3SelectPayment(FormView):
    template_name = 'orders/step3-select-payment.html'
    form_class = SelectPaymentForm
    success_url = reverse_lazy('orders:confirmation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_step'] = 'step3'
        return context

    def form_valid(self, form):
        payment_method = form.cleaned_data['payment_method']
        order_data = cache.get('order_data', {})
        order_data['payment_method'] = payment_method
        cache.set('order_data', order_data, None)
        return super().form_valid(form)


class Step4OrderConfirmation(TemplateView):
    template_name = 'orders/step4-order_confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=self.request.user.pk)
        order_data = cache.get('order_data', {})
        delivery_method = order_data.get('delivery_method')
        city = order_data.get('city')
        address = order_data.get('address')
        payment_method = order_data.get('payment_method')
        order, created = Order.objects.get_or_create(
            user=user,
            delivery_method=delivery_method,
            payment_method=payment_method,
            city=city,
            address=address,
        )
        context['order'] = order
        context['user'] = user
        context['current_step'] = 'step4'

        return context
