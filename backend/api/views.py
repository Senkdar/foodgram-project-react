from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .permissions import AuthorOrReadOnlyPermission
from api.filters import RecipesFilter
from .serializers import (
    FavoritesSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    ShoppingCartSerializer,
    TagsSerializer,
)
from recipes.models import (
    Favorites,
    Ingredients,
    Recipes,
    RecipesIngredients,
    ShoppingCart,
    Tags,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilter
    permission_classes = [AuthorOrReadOnlyPermission, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = RecipesIngredients.objects.filter(
            recipe__shopping_cart__user=request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                Sum('amount')
            )
        text_in_file = 'Список покупок: \n'
        for item in ingredients:
            text_in_file += (
                f"{item['ingredient__name']} — "
                f"{item['amount__sum']} "
                f"{item['ingredient__measurement_unit']} \n"
            )
        response = HttpResponse(text_in_file, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response


class FavoriteListViewSet(generics.ListAPIView):
    """Вьюсет для списка избранного."""
    serializer_class = FavoritesSerializer

    def get_queryset(self):
        new_queryset = Favorites.objects.filter(user=self.request.user)
        return new_queryset


class ShoppingCartViewSet(APIView):
    """Вью для списка покупок."""
    serializer_class = ShoppingCartSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipes, id=self.kwargs.get('recipe_id'))
        shopping_cart = ShoppingCart.objects.get_or_create(
            user=user, recipe=recipe
        )
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


class FavoriteViewSet(APIView):
    """Вью для создания/удаления избранного."""
    serializer_class = FavoritesSerializer
    permission_classes = [AuthorOrReadOnlyPermission]

    def post(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipes, id=self.kwargs.get('recipe_id'))
        favorite = Favorites.objects.get_or_create(user=user, recipe=recipe)
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


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    serializer_class = TagsSerializer
    queryset = Tags.objects.all()
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    serializer_class = IngredientSerializer
    queryset = Ingredients.objects.all()
    permission_classes = (AllowAny,)
    SearchFilter.search_param = 'name'
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)
