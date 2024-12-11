from django.contrib import admin

from .models import FavoriteRecipe, Ingredient, Recipe, RecipeIngredients, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavouriteAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    search_help_text = 'Поиск по названию'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'author__username')
    search_help_text = 'Поиск по названию и автору'
    filter_horizontal = ('tags',)
    list_filter = ('tags', 'author__username')
    readonly_fields = ('in_favorites',)

    @admin.display(description='Число добавления в избранное')
    def in_favorites(self, recipe):
        return FavoriteRecipe.objects.filter(recipe=recipe).count()
