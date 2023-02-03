# from . import models
# import os
# import sys
# from django.conf import settings
# from foodgram.settings import BASE_DIR
# settings.configure()
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")
# sys.path.append(BASE_DIR)

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics
from api.models import (
    Ingredients,
    User,
    Recipes,
    Tags,
    RecipesIngredients,
    Follows,
    Favorites,
)
from .serializers import (
    GetRecipesSerializer,
    IngredientSerilizer,
    UserSerializer,
    RecipeSerializer,
    RecipeIngredientSerializer,
    TagSerializer,
    FollowSerializer,
    FollowListSerializer,
    FavoritesSerializer,
    )


class FollowsViewSet(viewsets.ModelViewSet):

    serializer_class = FollowSerializer

    def get_queryset(self):
        author_id = self.kwargs.get('user_id')
        new_queryset = Follows.objects.filter(
            author=author_id, user=self.request.user
        )
        return new_queryset

    def perform_create(self, serializer):
        author_id = self.kwargs.get('user_id')
        author = get_object_or_404(User, id=author_id)
        serializer.save(user=self.request.user, author=author)


class FollowListViewSet(generics.ListAPIView):

    serializer_class = FollowListSerializer

    def get_queryset(self):
        new_queryset = User.objects.filter(following__user=self.request.user)
        return new_queryset


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    print(queryset)
    serializer_class = UserSerializer

    @action(detail=False)
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipesSerializer
        return RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):

    serializer_class = TagSerializer
    queryset = Tags.objects.all()


class IngredientViewSet(viewsets.ModelViewSet):

    serializer_class = IngredientSerilizer
    queryset = Ingredients.objects.all()


class RecipesIngredientsViewSet(viewsets.ModelViewSet):

    serializer_class = RecipeIngredientSerializer
    queryset = RecipesIngredients.objects.all()


class FavoriteViewSet(viewsets.ModelViewSet):

    serializer_class = FavoritesSerializer

    def get_queryset(self):
        recipe_id = get_object_or_404(Recipes, pk=self.kwargs.get('recipe_id'))
        return Favorites.objects.filter(user=self.request.user, recipe=recipe_id)

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipes, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)