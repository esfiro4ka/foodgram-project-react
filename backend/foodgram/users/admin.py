from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription, User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username',)
    list_filter = ('email', 'username',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription)
