from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.aggregates import Count
from django.utils.safestring import mark_safe

from .models import (FavoriteRecipe, Follow, Ingredient,
                     Recipe, RecipeIngredients, Tag, ShortUrl, User)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')
    search_help_text = 'Поиск по названию и слагу'

    @admin.display(description='Число рецептов')
    def recipes_count(self, tag):
        return tag.recipes.count()


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavouriteAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    search_help_text = 'Поиск по названию и ед. измерения'
    list_filter = ('measurement_unit',)


class IngredientsInLine(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time',
        'author', 'recipe_tags', 'in_favorites',
        'recipe_ingredients', 'recipe_img'
    )
    list_display_links = ('name',)
    search_fields = ('name', 'author__username')
    search_help_text = 'Поиск по названию и автору'
    filter_horizontal = ('tags',)
    inlines = [IngredientsInLine]
    list_filter = ('tags', 'author__username')
    image_style = 'height:70px;'

    @admin.display(description='Избранное')
    def in_favorites(self, recipe):
        return recipe.favorite_recipes.count()

    @mark_safe
    @admin.display(description='Картинка')
    def recipe_img(self, recipe):
        img_src = recipe.image.url if recipe.image else ''
        return f'<img src="{img_src}" style="{self.image_style}"/>'

    def recipe_get_list(self, field):
        return (
            '<lu>' + "".join(
                [f'<li>{entry.name}</li>' for entry in field.all()]
            ) + '</lu>'
        )

    @mark_safe
    @admin.display(description='Теги')
    def recipe_tags(self, recipe):
        return self.recipe_get_list(recipe.tags)

    @mark_safe
    @admin.display(description='Продукты')
    def recipe_ingredients(self, recipe):
        return self.recipe_get_list(recipe.ingredients)


@admin.register(ShortUrl)
class ShortUrlAdmin(admin.ModelAdmin):
    pass


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_display_links = None


class UserFilter(admin.SimpleListFilter):
    options = [('1', 'да'),
               ('0', 'нет')]

    def lookups(self, request, model_admin):
        return self.options

    def queryset(self, request, queryset):
        if self.value() not in dict(self.options):
            return queryset
        filter_expr = {'count__gt': 0} if self.value() == '1' else {'count': 0}
        return queryset.annotate(
            count=Count(self.count_expression)
        ).filter(**filter_expr)


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
    list_display = ('avatar_img', 'username', 'email', 'full_name', 'is_staff')
    list_display_links = ('username', 'email')
    list_filter = UserAdmin.list_filter + (
        HasRecipesFilter, HasFollowersFilter, HasFollowsFilter
    )
    avatar_style = 'height:70px;'

    @admin.display(description='Имя')
    def full_name(self, user):
        return user.get_full_name()

    @mark_safe
    @admin.display(description='Аватар')
    def avatar_img(self, user):
        img_src = user.avatar.url if user.avatar else ''
        return f'<img src="{img_src}" style="{self.avatar_style}">'

    @admin.display(description='Подписчиков')
    def followers(self, user):
        return user.authors.count()

    @admin.display(description='Подписок')
    def users_following(self, user):
        return user.followers.count()

    @admin.display(description='Опубликованных рецептов')
    def recipes(self, user):
        return user.recipes.count()
