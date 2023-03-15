from django.shortcuts import get_object_or_404
import webcolors
from rest_framework import serializers

from users.serializers import MyUserSerializer

from .models import (
        Ingredients,
        ShoppingCart,
        Recipes,
        RecipesIngredients,
        Tags,
        Favorites,
    )


class Hex2NameColor(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagsSerializer(serializers.ModelSerializer):

    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagsSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    is_in_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = '__all__'

    def get_ingredients(self, obj):
        queryset = RecipesIngredients.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(queryset, many=True).data

    def get_is_in_favorite(self, obj):
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

    author = MyUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all()
    )

    class Meta:
        model = Recipes
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name',
            'description', 'cooking_time', 'author'
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            ingredient = get_object_or_404(Ingredients, name=ingredient_id)
            RecipesIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        for tag in tags_data:
            recipe.tags.add(tag)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoritesSerializer(serializers.ModelSerializer):

    recipe = ShortRecipeSerializer(read_only=True)

    class Meta:
        model = Favorites
        fields = ('recipe',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret['recipe']


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')
