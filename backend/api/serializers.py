import webcolors
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404


from .models import (
        Ingredients,
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


class FollowSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    # author = serializers.SerializerMethodField()

    # def get_author(self, obj):
    #     return User.objects.filter(
    #         id=obj.id
    #     )

    class Meta:
        model = Follows
        fields = ('user', 'author')

        validators = [
            UniqueTogetherValidator(
                queryset=Follows.objects.all(),
                fields=('user', 'author'),
                message='Нельзя подписаться на автора два раза'
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data['author']:
            raise serializers.ValidationError(
                'Нельзя оформить подписку на себя')
        return data


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

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


class FollowListSerializer(UserSerializer):

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


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetTagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = ('__all__')


class GetRecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = '__all__'

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            RecipesIngredients.objects.filter(recipe=obj).all(), many=True
        ).data


class RecipeSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientSerializer(many=True)

    def create(self, validated_data):
        print(validated_data)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        for tag in tags:
            current_tag = get_object_or_404(
                Tags, pk=tag.id)
            RecipesTags.objects.get_or_create(
                tag=current_tag, recipe=recipe)
        for ingredient in ingredients:
            # ingredient_id = ingredient['id']
            current_ingredient = get_object_or_404(
                Ingredients, id=ingredient.get('id')
            )
            RecipesIngredients.objects.get_or_create(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=current_ingredient
            )
        return recipe

    # def to_representation(self, instance):
    #     return GetRecipesSerializer(instance).data

    class Meta:
        model = Recipes
        fields = '__all__'


class FavoritesSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Favorites
        fields = ('recipe', 'user')
