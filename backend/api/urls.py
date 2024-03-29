from django.urls import path, include
from rest_framework import routers

from .views import (
        FavoriteViewSet,
        FavoriteListViewSet,
        IngredientViewSet,
        RecipeViewSet,
        ShoppingCartViewSet,
        TagViewSet,
    )


router = routers.DefaultRouter()

router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
urlpatterns = [
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view(),
        name='favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view(),
        name='shopping_cart'
    ),
    path(
        'users/me/favorite/',
        FavoriteListViewSet.as_view(),
    ),
    path('', include(router.urls)),
]
