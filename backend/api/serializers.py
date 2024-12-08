from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    FavoriteRecipe, Ingredient,
    Recipe, RecipeIngredients,
    Tag, ShoppingCartRecipe
)
from users.models import User, Follow

from .constants import RECIPIES_LIMIT_DEFAULT


class AvatarSerializer(serializers.ModelSerializer):
    """Сериалайзер аватарки."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class FoodgramUserSerializer(UserSerializer):
    """Сериалайзер пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, user):
        if 'request' in self.context and (
            self.context['request'].user.is_authenticated
        ):
            return Follow.objects.filter(
                user=self.context['request'].user, author=user
            ).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер игредиентов для рецептов."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер рецептов."""

    author = FoodgramUserSerializer()
    ingredients = IngredientForRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def check_recipe(self, recipe, recipe_model):
        if 'request' in self.context and (
            self.context['request'].user.is_authenticated
        ):
            return recipe_model.objects.filter(
                user=self.context['request'].user, recipe=recipe
            ).exists()
        return False

    def get_is_favorited(self, recipe):
        return self.check_recipe(recipe, FavoriteRecipe)

    def get_is_in_shopping_cart(self, recipe):
        return self.check_recipe(recipe, ShoppingCartRecipe)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиента для рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.FloatField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания рецептов."""

    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.save()

        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient['id']
            amount = recipe_ingredient['amount']
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()

        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient['id']
            amount = recipe_ingredient['amount']
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления в избранное."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowingSerializer(FoodgramUserSerializer):
    """Сериалайзер подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_recipes(self, user):
        recipies_limit = self.context['request'].GET.get(
            'recipes_limit', default=''
        )

        recipies_limit = (
            int(recipies_limit) if recipies_limit.isdecimal()
            else RECIPIES_LIMIT_DEFAULT
        )
        return FavoriteSerializer(
            user.recipes.all()[:recipies_limit],
            many=True
        ).data

