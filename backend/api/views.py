from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status

from api.models import (
    Ingredients,
    ShoppingCart,
    User,
    Recipes,
    Tags,
    RecipesIngredients,
    Follows,
    Favorites,
)
from .serializers import (
    GetRecipesSerializer,
    IngredientSerializer,
    MyUserSerializer,
    RecipeSerializer,
    RecipeIngredientSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    FollowSerializer,
    FollowListSerializer,
    FavoritesSerializer,
    )


class UserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = ()


class FavoriteListViewSet(generics.ListAPIView):

    serializer_class = FavoritesSerializer

    def get_queryset(self):
        new_queryset = Favorites.objects.filter(user=self.request.user)
        return new_queryset


class FollowListViewSet(generics.ListAPIView):

    serializer_class = FollowListSerializer

    def get_queryset(self):
        new_queryset = User.objects.filter(following__user=self.request.user)
        return new_queryset


class FollowsViewSet(APIView):

    serializer_class = FollowSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('user_id'))

        if user == author:
            return Response(
                {'error': 'Вы не можете подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follows.objects.filter(user=user, author=author).exists():
            return Response(
                {'error': 'Вы уже подписаны на пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follows.objects.create(user=user, author=author)
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('user_id'))

        followed = Follows.objects.filter(user=user, author=author)
        if followed:
            followed.delete()
            return Response(
                {'success': 'Подписка успешно удалена'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'error': 'Вы не подписаны на пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipesSerializer
        return RecipeSerializer


class ShoppingCartViewSet(APIView):

    serializer_class = ShoppingCartSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipes, id=self.kwargs.get('recipe_id'))

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Этот рецепт уже есть в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart = ShoppingCart.objects.create(user=user, recipe=recipe)
        return Response(
            FavoritesSerializer(shopping_cart).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):

        user = request.user
        recipe = get_object_or_404(Recipes, id=self.kwargs.get('recipe_id'))

        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Этого рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            {'success': 'Рецепт удален из списка покупок'},
            status=status.HTTP_201_CREATED
        )



class TagViewSet(viewsets.ModelViewSet):

    serializer_class = TagSerializer
    queryset = Tags.objects.all()


class IngredientViewSet(viewsets.ModelViewSet):

    serializer_class = IngredientSerializer
    queryset = Ingredients.objects.all()


class RecipesIngredientsViewSet(viewsets.ModelViewSet):

    serializer_class = RecipeIngredientSerializer
    queryset = RecipesIngredients.objects.all()


class FavoriteViewSet(APIView):

    serializer_class = FavoritesSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipes, id=self.kwargs.get('recipe_id'))

        if Favorites.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Этот рецепт уже есть в списке избранного'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite = Favorites.objects.create(user=user, recipe=recipe)
        return Response(
            FavoritesSerializer(favorite).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):

        user = request.user
        recipe = get_object_or_404(Recipes, id=self.kwargs.get('recipe_id'))

        if not Favorites.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Этого рецепта нет в списке избранного'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorites.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            {'success': 'Рецепт удален из избранного'},
            status=status.HTTP_201_CREATED
        )
