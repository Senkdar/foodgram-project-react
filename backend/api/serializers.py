from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
import webcolors

from users.serializers import MyUserSerializer
from recipes.models import (
        Favorites,
        Ingredients,
        Recipes,
        RecipesIngredients,
        ShoppingCart,
        Tags,
    )


class Hex2NameColor(serializers.Field):
    """Настройка для выбора цвета тега."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецепта и ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=0.1, max_value=5000)

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецепта."""

    tags = TagsSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = '__all__'

    def get_ingredients(self, obj):
        queryset = RecipesIngredients.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorites.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    author = MyUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name',
            'text', 'cooking_time', 'author'
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        ingredients_list = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            ingredient = get_object_or_404(Ingredients, name=ingredient_id)
            ingredients_list.append(RecipesIngredients(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            ))
        RecipesIngredients.objects.bulk_create(ingredients_list)
        for tag in tags_data:
            recipe.tags.add(tag)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags_data:
            instance.tags.set(tags_data)
        if ingredients_data:
            RecipesIngredients.objects.filter(recipe=instance).delete()
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get('id')
                ingredient = get_object_or_404(Ingredients, name=ingredient_id)
                RecipesIngredients.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
        instance.save()
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецепта в полях других моделей."""

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для списка избранного."""

    recipe = ShortRecipeSerializer(read_only=True)

    class Meta:
        model = Favorites
        fields = ('recipe',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')
