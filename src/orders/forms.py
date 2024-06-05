from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User


class UserDataForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'email', 'phone')


class PasswordForm(forms.Form):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Enter Password Again', widget=forms.PasswordInput)

    def clean_password2(self):

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

