from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django_short_url.views import get_surl

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientsFilter, RecipesFilter
from .models import (
    FavoriteRecipe, Ingredient,
    Recipe, RecipeIngredients,
    Tag, ShoppingCartRecipe
)
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer, RecipeSerializer, TagSerializer
)
from api.pagintation import CustomPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет рецетов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    # def get_serializer_class(self):
    #     if self.action in ('list', 'retrieve'):
    #         return RecipeSerializer
    #     return CreateRecipeSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='favorite',
    )
    def add_to_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if request.method == 'POST':
            favorite, created = FavoriteRecipe.objects.get_or_create(
                recipe=recipe,
                user=user
            )
            if created:
                return Response(
                    FavoriteSerializer(recipe).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': f'Рецепт {recipe.name} уже добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            if FavoriteRecipe.objects.filter(
                recipe=recipe, user=user
            ).exists():
                FavoriteRecipe.objects.get(recipe=recipe, user=user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'Рецепта {recipe.name} нет в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=True,
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        return Response({
            'short-link':
            request.build_absolute_uri(
                get_surl(
                    request.build_absolute_uri(
                        '/recipes/%s/' % pk
                    )
                )
            )
        }, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        shopping_list = {}
        for ingredient in RecipeIngredients.objects.filter(
            recipe__is_in_shopping_cart__user=self.request.user
        ):
            key = ingredient.ingredient.name
            if key in shopping_list:
                shopping_list[key][0] += ingredient.amount
            else:
                shopping_list[key] = [
                    ingredient.amount, ingredient.ingredient.measurement_unit
                ]
        shopping_text = 'Список покупок:\n'
        for key in shopping_list:
            shopping_text += (
                f'{key} {shopping_list[key][0]} {shopping_list[key][1]}\n'
            )
        return HttpResponse(shopping_text, content_type='text/plain')

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if request.method == 'POST':
            favorite, created = ShoppingCartRecipe.objects.get_or_create(
                recipe=recipe,
                user=user
            )
            if created:
                return Response(
                    FavoriteSerializer(recipe).data,
                    status=status.HTTP_201_CREATED
                )
            return Response({
                'errors':
                f'Рецепт {recipe.name} уже добавлен в список покупок.'
            }, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if ShoppingCartRecipe.objects.filter(
                recipe=recipe, user=user
            ).exists():
                ShoppingCartRecipe.objects.get(
                    recipe=recipe, user=user
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'Рецепта {recipe.name} нет в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)
