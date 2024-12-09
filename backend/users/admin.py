from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.aggregates import Count

from .models import Follow, User
from recipes.models import Recipe


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass


class UserFilter(admin.SimpleListFilter):

    def lookups(self, request, model_admin):
        return [
            ('1', 'да'),
            ('0', 'нет'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.annotate(
                count=Count(self.count_expression)
            ).filter(count__gt=0)
        if self.value() == '0':
            return queryset.annotate(
                count=Count(self.count_expression)
            ).filter(count=0)
        return queryset


class HasRecipesFilter(UserFilter):
    title = 'есть рецепты'
    parameter_name = 'has_recipes'
    count_expression = 'recipes'


class HasFollowersFilter(UserFilter):
    title = 'есть подписчики'
    parameter_name = 'has_followers'
    count_expression = 'authors'


class HasFollowsFilter(UserFilter):
    title = 'есть подписки'
    parameter_name = 'has_follows'
    count_expression = 'followers'


@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по автору и электронной почте'
    readonly_fields = ('followers', 'users_following', 'recipes')
    fieldsets = UserAdmin.fieldsets + (('Stats', {'fields': readonly_fields}),)
    list_filter = UserAdmin.list_filter + (
        HasRecipesFilter, HasFollowersFilter, HasFollowsFilter
    )

    @admin.display(description='Количество подписчиков')
    def followers(self, user):
        return Follow.objects.filter(author=user).count()

    @admin.display(description='Количество подписок')
    def users_following(self, user):
        return Follow.objects.filter(user=user).count()

    @admin.display(description='Количество опубликованных рецептов')
    def recipes(self, user):
        return Recipe.objects.filter(author=user).count()
