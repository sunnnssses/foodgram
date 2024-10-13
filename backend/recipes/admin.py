from django.contrib import admin

from .models import Tag, FavoriteRecipe, Ingredient, Recipe, RecipeIngredients


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredients)
admin.site.register(FavoriteRecipe)
