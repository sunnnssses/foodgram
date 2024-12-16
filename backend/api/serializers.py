from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .constants import PAGE_SIZE
from recipes.constants import MIN_COOKING_TIME, MIN_AMOUNT
from recipes.models import (
    Favorite, Follow, Ingredient,
    Recipe, RecipeIngredients,
    Tag, ShoppingCart, User
)


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
            *UserSerializer.Meta.fields,
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, user):
        return 'request' in self.context and (
            self.context['request'].user.is_authenticated
        ) and (
            Follow.objects.filter(
                user=self.context['request'].user, author=user
            ).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


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


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер рецептов."""

    author = FoodgramUserSerializer()
    ingredients = IngredientForRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date', )
        read_only_fields = (
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

    def __init__(self, *args, **kwargs):
        is_short = kwargs.pop('short', False)
        super().__init__(*args, **kwargs)
        if is_short:
            short_fields = set(['id', 'name', 'image', 'cooking_time'])
            for field in set(self.fields) - short_fields:
                self.fields.pop(field)

    def check_recipe(self, recipe, recipe_model):
        return 'request' in self.context and (
            self.context['request'].user.is_authenticated
        ) and recipe_model.objects.filter(
            user=self.context['request'].user, recipe=recipe
        ).exists()

    def get_is_favorited(self, recipe):
        return self.check_recipe(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self.check_recipe(recipe, ShoppingCart)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиента для рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания рецептов."""

    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME
    )

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

    @staticmethod
    def set_ingredients(recipe, recipe_ingredients):
        RecipeIngredients.objects.bulk_create(
            RecipeIngredients(
                recipe=recipe,
                ingredient=recipe_ingredient['id'],
                amount=recipe_ingredient['amount']
            ) for recipe_ingredient in recipe_ingredients
        )

    def create(self, validated_data):
        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, recipe_ingredients)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        recipe_ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.set_ingredients(instance, recipe_ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return GetRecipeSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для сокращённого представления."""

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
            *FoodgramUserSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, user):
        try:
            recipies_limit = int(self.context['request'].GET.get(
                'recipes_limit', default=10**10
            ))
        except (TypeError, ValueError):
            recipies_limit = 10**10

        return ShortRecipeSerializer(
            user.recipes.all()[:recipies_limit],
            many=True
        ).data
