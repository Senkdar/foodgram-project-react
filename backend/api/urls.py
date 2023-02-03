from django.urls import path, include
from rest_framework import routers

from .views import (
        IngredientViewSet,
        RecipesIngredientsViewSet,
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
router.register(
    r'^users/(?P<user_id>\d+)/subscribe',
    viewset=FollowsViewSet,
    basename='subscribe'
)
router.register(
    r'^recipes/(?P<recipe_id>\d+)/favorite',
    viewset=FavoriteViewSet,
    basename='favotite'
)

urlpatterns = [
    path(
        'users/subscribtions/',
        FollowListViewSet.as_view(),
    ),
    path('', include(router.urls)),
]
