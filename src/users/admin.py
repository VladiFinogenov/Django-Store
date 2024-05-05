from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm

    list_display = ('username', 'email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (
            'first_name',
            'last_name',
            'avatar',
        )
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(CustomUser, CustomUserAdmin)