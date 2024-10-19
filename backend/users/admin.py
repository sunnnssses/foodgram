from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User


admin.site.register(Follow)


@admin.register(User)
class UsersAdmin(UserAdmin):
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по автору и электронной почте'
