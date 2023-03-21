from django.urls import path, include
from rest_framework import routers

from users.views import (
        CustomUserViewSet,
        FollowListViewSet,
        FollowsViewSet,
    )

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')

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
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
