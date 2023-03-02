import webcolors
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404

from .models import (
        Ingredients,
        ShoppingCart,
        User,
        Recipes,
        RecipesIngredients,
        RecipesTags,
        Tags,
        Follows,
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


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class MyUserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        return Follows.objects.filter(
            user=self.context['request'].user,
            author=obj.id
        ).exists()


class FollowSerializer(MyUserSerializer):

    # recipes = serializers.SerializerMethodField(read_only=True)
    # recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed',)

    # def get_recipes(self, obj):
    #     ...


class FollowListSerializer(MyUserSerializer):

    class Meta:

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class TagsSerializer(serializers.ModelSerializer):

    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug',)


class GetRecipesSerializer(serializers.ModelSerializer):

    tags = TagsSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = '__all__'

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            RecipesIngredients.objects.filter(recipe=obj).all(), many=True
        ).data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:

        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(source='ingredient.id', read_only=True)
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):

    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        print(ingredients_data)
        for tag in tags_data:
            recipe.tags.add(tag)
        for ingredient_data in ingredients_data:
            RecipesIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
        return recipe

    class Meta:
        model = Recipes
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'description',
            'cooking_time'
        )


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
        fields = ('recipe',)
