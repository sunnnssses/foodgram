import random

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from foodgram.constants import (
    CHARACTERS, EMAIL_LENGTH, INGREDIENT_LENGTH,
    MIN_AMOUNT, MIN_COOKING_TIME, RECIPE_LENGTH,
    SHORT_URL_LENGTH, SLUG_REGEX, TAG_LENGTH,
    UNIT_LENGTH, USERNAME_LENGTH, USERNAME_REGEX
)


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        validators=[RegexValidator(regex=USERNAME_REGEX)],
    )
    first_name = models.CharField(max_length=USERNAME_LENGTH)
    last_name = models.CharField(max_length=USERNAME_LENGTH)
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_LENGTH,
        verbose_name='email'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(max_length=TAG_LENGTH, verbose_name='Название')
    slug = models.SlugField(
        max_length=TAG_LENGTH,
        unique=True,
        verbose_name='Слаг',
        validators=[RegexValidator(regex=SLUG_REGEX)]
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('slug', )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=INGREDIENT_LENGTH,
                            verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=UNIT_LENGTH,
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
    name = models.CharField(max_length=RECIPE_LENGTH, verbose_name='Название')
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
        validators=[MinValueValidator(MIN_COOKING_TIME)]
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
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(MIN_AMOUNT)])

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
        default_related_name = 'highlihgted_recipes'
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
        default_related_name = 'favorite_recipes'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCartRecipe(BaseUserRecipeModel):
    """Модель корзины."""

    class Meta(BaseUserRecipeModel.Meta):
        default_related_name = 'recipes_in_shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class ShortUrl(models.Model):
    """Модель для коротких ссылок."""

    full_url = models.URLField(unique=True)
    short_url = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_date',)

    def save(self, *args, **kwargs):
        if not self.short_url:
            while True:
                self.short_url = ''.join(
                    random.choices(
                        CHARACTERS,
                        k=SHORT_URL_LENGTH
                    )
                )
                if not ShortUrl.objects.filter(
                    short_url=self.short_url
                ).exists():
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.short_url} -> {self.full_url}'


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
