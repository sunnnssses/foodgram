from django.db.models import Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.validators import ValidationError

from recipes.models import (
    Favorite, Follow, Ingredient,
    Recipe, RecipeIngredients,
    Tag, ShoppingCart, User
)

from .filters import IngredientsFilter, RecipesFilter
from .serializers import (
    AvatarSerializer, FollowingSerializer,
    FoodgramUserSerializer, GetRecipeSerializer,
    IngredientSerializer, RecipeSerializer,
    ShortRecipeSerializer, TagSerializer
)
from .pagintation import Pagination
from .utils import get_shopping_list


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
    serializer_class = GetRecipeSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='favorite',
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if request.method == 'POST':
            return self.highlight_recipe(
                Favorite, recipe, user, 'избранное'
            )
        return self.unhighlight_recipe(Favorite, recipe, user)

    @action(
        methods=['get'],
        detail=True,
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            raise Http404("Рецепт не найден.")
        return Response({
            'short-link':
            request.build_absolute_uri(reverse('recipes:short_url', args=[pk]))
        }, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        return FileResponse(
            get_shopping_list(
                RecipeIngredients.objects.filter(
                    recipe__recipes_in_shopping_cart__user=self.request.user
                ).values(
                    'ingredient__name',
                    'ingredient__measurement_unit'
                ).annotate(sum=Sum('amount')).order_by('ingredient__name'),
                Recipe.objects.filter(
                    recipes_in_shopping_cart__user=self.request.user
                )
            ),
            content_type='text/plain'
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if request.method == 'POST':
            return self.highlight_recipe(
                ShoppingCart, recipe, user, 'покупки'
            )
        return self.unhighlight_recipe(ShoppingCart, recipe, user)

    def highlight_recipe(self, model, recipe, user, destination):
        _, created = model.objects.get_or_create(recipe=recipe, user=user)
        if not created:
            raise ValidationError(
                f'Рецепт {recipe.name} уже добавлен в {destination}.'
            )
        return Response(
            ShortRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def unhighlight_recipe(self, model, recipe, user):
        get_object_or_404(model, recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FoodgramUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    pagination_class = Pagination
    permission_classes = (AllowAny,)

    def get_permissions(self):
        if (self.action == 'me'):
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        methods=['put', 'delete'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def set_avatar(self, request):
        instance = self.get_instance()
        if request.method == 'PUT':
            data = request.data
        else:
            data = {'avatar': None}
        serializer = AvatarSerializer(instance, data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        if request.method == 'PUT':
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        pagination_class=Pagination,
        url_path='subscriptions',
    )
    def get_subscriptions(self, request):
        return self.get_paginated_response(
            FollowingSerializer(
                self.paginate_queryset(
                    User.objects.filter(authors__user=self.request.user)
                ),
                many=True,
                context={'request': request}
            ).data
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='subscribe',
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = self.request.user
        if request.method == 'DELETE':
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if author == user:
            raise ValidationError(
                detail={'errors': 'Нельзя подписаться на себя'}
            )
        _, created = Follow.objects.get_or_create(
            user=user,
            author=author
        )
        if not created:
            raise ValidationError(
                detail={
                    'errors':
                    f'Вы уже подписаны на пользователя {author.username}.'
                })
        return Response(
            FollowingSerializer(
                author,
                context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )


