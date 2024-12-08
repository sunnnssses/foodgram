from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(max_length=64, unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=256, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_unit',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель рецептов."""

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(max_length=256, verbose_name='Название')
    image = models.ImageField('Картинка', upload_to='recipes_images')
    text = models.TextField(verbose_name='Текстовое описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        default_related_name = 'recipes'
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return f'Рецепт {self.name[:50]} автора {self.author}'


class RecipeIngredients(models.Model):
    """Модель продуктов для рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )
    amount = models.FloatField(
        verbose_name='Количество',
        validators=[MinValueValidator(0.1)])

    class Meta:
        default_related_name = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'], name='unique ingredient'
            )
        ]
        verbose_name = 'продукт для рецепта'
        verbose_name_plural = 'продукт для рецептов'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'
    

class BaseUserRecipeModel(models.Model):
    """Базовая модель для добавления рецептов в списки."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='%(app_label)s_%(class)s_recipe_user',
            )
        ]
        abstract = True

    def __str__(self):
        return f'{self.user} добавил {self.recipe}'


class FavoriteRecipe(BaseUserRecipeModel):
    """Модель избранного."""

    class Meta(BaseUserRecipeModel.Meta):
        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCartRecipe(BaseUserRecipeModel):
    """Модель корзины."""

    class Meta(BaseUserRecipeModel.Meta):
        default_related_name = 'in_shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

