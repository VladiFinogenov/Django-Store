from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Enter Password Again', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'phone')

    def clean_password2(self):
        # Убедимся, что две записи пароля совпадают

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Сохраним предоставленный пароль в хэшированном формате
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Форма обновления данных пользователя
    """

    username = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    avatar = forms.ImageField()
    birth_date = forms.DateField(
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите дату рождения',
                'type': 'date'
            }),
        required=False
    )

    class Meta:
        model = User
        fields = ('avatar', 'first_name', 'last_name', 'birth_date')


class UserRegisterForm(UserCreationForm):
    """
    Переопределенная форма регистрации пользователей
    """

    class Meta(UserCreationForm.Meta):
        fields = ['email', 'phone']

    def clean_email(self):
        """
        Проверка email на уникальность
        """

        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Такой email уже используется в системе')
        return email

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы регистрации
        """

        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            "placeholder": "Пароль",
            'name': "pass",
            'id': "name",
        })
        self.fields['password2'].widget.attrs.update({
            "placeholder": "Повторите пароль"
        })
        self.fields['email'].widget.attrs.update({
            'name': "login",
            'id': "name",
            'placeholder': 'E-mail',
            'class': 'user-input'
        })


class UserLoginForm(AuthenticationForm):
    """
    Форма авторизации на сайте
    """

    def confirm_login_allowed(self, user):
        if not user.is_verified:
            raise forms.ValidationError(
                'Email is not verified'
            )

    class Meta:
        model = User
        fields = ['password', 'recaptcha']

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы авторизации
        """

        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Логин пользователя'
        self.fields['password'].widget.attrs['placeholder'] = 'Пароль пользователя'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['username'].label = 'Log in'
        self.fields['username'].widget.attrs['autofocus'] = False
