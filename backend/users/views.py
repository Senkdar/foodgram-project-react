from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status

from users.models import (
    User,
    Follows,
)
from .serializers import (
    CreateUserSerializer,
    MyUserSerializer,
    FollowSerializer,
    FollowListSerializer,
    )


class CustomUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return MyUserSerializer
        return CreateUserSerializer


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
