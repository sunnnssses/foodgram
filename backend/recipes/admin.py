from django.contrib import admin

from .models import FavoriteRecipe, Ingredient, Recipe, RecipeIngredients, Tag

admin.site.register(Tag)
admin.site.register(RecipeIngredients)
admin.site.register(FavoriteRecipe)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    search_help_text = 'Поиск по названию'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'author__username')
    search_help_text = 'Поиск по названию и автору'

    def in_favorites(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()
