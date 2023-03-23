from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import CustomPagination
from .serializers import (
    CreateUserSerializer,
    FollowSerializer,
    MyUserSerializer,
)
from users.models import (
    Follows,
    User,
)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей."""

    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return MyUserSerializer
        return CreateUserSerializer


class FollowListViewSet(generics.ListAPIView):
    """Вью для списка подписок."""

    serializer_class = FollowSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        new_queryset = User.objects.filter(following__user=self.request.user)
        return new_queryset


class FollowsViewSet(APIView):
    """Вью для создания/удаления подписок."""

    serializer_class = FollowSerializer
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('user_id'))

        if user == author:
            return Response(
                {'error': 'Вы не можете подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follows.objects.get_or_create(user=user, author=author)
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
