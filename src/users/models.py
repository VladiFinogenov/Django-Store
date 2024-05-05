from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import FileExtensionValidator
from PIL import Image
from django.db import models


def profile_avatar_directory_path(instance: "CustomUser", filename: str):
    return 'images/avatar/user_{name}/{filename}'.format(
        name=instance.username,
        filename=filename
    )


class CustomUser(AbstractUser):

    phone_regex = RegexValidator(
        regex=r'^((\+7)|8)/d{10}$',
        message='Phone number must be entered in the format: "+79999999999" or "89999999999" '
    )

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12, unique=True, validators=[phone_regex])
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to=profile_avatar_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))],
    )
    birth_date = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):

        # Сохранение аватарки с разрешением 276 x 276
        if self.avatar and (self.avatar.width > 276 or self.avatar.height > 276):
            img = Image.open(self.avatar.path)
            new_img = (276, 276)
            img.thumbnail(new_img)
            img.save(self.avatar.path)

    def __str__(self) -> str:
        return self.username
