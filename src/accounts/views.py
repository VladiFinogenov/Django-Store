from django.views.generic import View, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserUpdateForm
from .forms import UserRegisterForm, UserLoginForm
from .models import User


class ProfileDetailView(DetailView):
    """
    Представление для просмотра профиля
    """

    model = User
    context_object_name = 'accounts'
    template_name = 'accounts/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Профиль пользователя: {self.request.user.username}'
        # author_posts = Post.custom.filter(author=self.object)

        # context['author_posts'] = author_posts

        return context


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
        # Вызов функции для обновления статуса пользователя
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
