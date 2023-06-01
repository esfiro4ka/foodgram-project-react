from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.models import TokenProxy
from users.models import Subscription, User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username',)
    list_filter = ('email', 'username',)


TokenProxy._meta.verbose_name = 'Токен'
TokenProxy._meta.verbose_name_plural = 'Токены'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription)
