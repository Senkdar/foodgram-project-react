from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tags(models.Model):
    """Модель тегов"""
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredients(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipes(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipesIngredients',
    )
    tags = models.ManyToManyField(
        Tags,
        through='RecipesTags',
    )
    image = models.ImageField(blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    cooking_time = models.SmallIntegerField(
        validators=[MinValueValidator(
            1, 'cooking time should be more than 1 minute')]
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipesTags(models.Model):
    """Промежуточная модель для связи рецептов и тегов"""
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)


class RecipesIngredients(models.Model):
    """Промежуточная модель для связи рецептов и количества ингредиентов"""
    recipe = models.ForeignKey(
        Recipes,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredients,
        related_name='amount',
        on_delete=models.CASCADE
    )
    amount = models.FloatField()

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'


class Favorites(models.Model):
    """Модель избранных рецептов"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    """Модель списка покупков"""
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
