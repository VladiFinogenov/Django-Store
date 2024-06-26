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
    full_name = forms.CharField(label='ФИО', required=False)
    email = forms.EmailField(label='Email', required=False)
    phone = forms.CharField(label='Телефон', required=False)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=False)
    avatar = forms.ImageField(label='Аватар', required=False)
    last_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    username = forms.CharField(widget=forms.HiddenInput(), required=False)
    middle_name = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'avatar', 'last_name', 'username', 'middle_name']

    def clean(self):
        cleaned_data = super().clean()
        full_name = cleaned_data.get('full_name')

        if full_name:
            names = full_name.split()
            if len(names) == 3:
                cleaned_data['last_name'] = names[0]
                cleaned_data['username'] = names[1]
                cleaned_data['middle_name'] = names[2]
            else:
                raise forms.ValidationError("Пожалуйста, введите Фамилию, Имя и Отчество через пробел.")

        return cleaned_data

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Размер аватара не должен превышать 2MB.")
        return avatar

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


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
