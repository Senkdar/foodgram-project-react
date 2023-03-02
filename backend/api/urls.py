from django.urls import path, include
from rest_framework import routers

from .views import (
        FavoriteListViewSet,
        IngredientViewSet,
        RecipesIngredientsViewSet,
        ShoppingCartViewSet,
        UserViewSet,
        RecipeViewSet,
        TagViewSet,
        FollowsViewSet,
        FollowListViewSet,
        FavoriteViewSet,
    )


router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipesingredients', RecipesIngredientsViewSet)
urlpatterns = [
    path(
        'users/subscribtions/',
        FollowListViewSet.as_view(),
    ),
    path(
        'users/<int:user_id>/subscribe/',
        FollowsViewSet.as_view(),
        name='subscribe'
    ),
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
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
