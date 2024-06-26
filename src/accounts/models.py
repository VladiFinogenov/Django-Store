from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from .manager import MyUserManager


def user_avatar_directory_path(instance: "User", filename: str):
    return 'accounts/avatar/user_{pk}/{filename}'.format(
        pk=instance.username,
        filename=filename
    )


class User(AbstractUser):

    phone_regex = RegexValidator(
        regex=r'^((\+7)|8)\d{10}$',
        message='Phone number must be entered in the format: "+79999999999" or "89999999999" ',
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(
        max_length=12,
        unique=True,
        validators=[phone_regex])
    avatar = models.ImageField(null=True, blank=True, upload_to=user_avatar_directory_path)
    birth_date = models.DateField(null=True, blank=True)
    is_seller = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = MyUserManager()

    def get_full_name(self):
        return f"{self.last_name} {self.username} {self.middle_name}"

    def __str__(self) -> str:
        return f"User(pk={self.pk}, user={self.first_name})"
