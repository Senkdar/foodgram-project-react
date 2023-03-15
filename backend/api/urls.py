from django.urls import path, include
from rest_framework import routers

from .views import (
        FavoriteListViewSet,
        IngredientViewSet,
        RecipesIngredientsViewSet,
        ShoppingCartViewSet,
        RecipeViewSet,
        TagViewSet,
        FavoriteViewSet,
    )


router = routers.DefaultRouter()

router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipesingredients', RecipesIngredientsViewSet)
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
