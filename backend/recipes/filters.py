from django_filters.rest_framework import FilterSet, filters

from .models import Ingredient, Tag, Recipe


class IngredientsFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='is_favorite')
    is_in_shopping_cart = filters.BooleanFilter(method='in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'tags')

    def is_favorite(self, queryset, name, value):
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(is_favorite__user=self.request.user)
        return queryset

    def in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(is_in_shopping_cart__user=self.request.user)
        return queryset
