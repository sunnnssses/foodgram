from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagintation import CustomPagination
from api.serializers import (
    AvatarSerializer, CustomUserSerializer, FollowingSerializer,
)
from .models import Follow, User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        methods=['put', 'delete'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def set_avatar(self, request):
        instance = self.get_instance()
        if request.method == 'PUT':
            serializer = AvatarSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            serializer = AvatarSerializer(instance, data={'avatar': None})
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        pagination_class=CustomPagination,
        url_path='subscriptions',
    )
    def get_subscriptions(self, request):
        return self.get_paginated_response(
            FollowingSerializer(
                self.paginate_queryset(
                    User.objects.filter(following__user=self.request.user)
                ),
                many=True,
                context={'request': request}
            ).data
        )
    
    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='subscribe',
    )
    def subscribe(self, request, id=None):
        following = get_object_or_404(User, id=id)
        user = self.request.user
        if request.method == 'POST':
            if following == user:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow, created = Follow.objects.get_or_create(
                user=user,
                following=following
            )
            if created:
                return Response(
                    FollowingSerializer(
                        following,
                        context={'request': request}
                    ).data,
                    status=status.HTTP_201_CREATED
                )
            return Response({
                'errors':
                f'Вы уже подписаны на пользователя {following.username}.'
            }, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if Follow.objects.filter(user=user, following=following).exists():
                Follow.objects.get(user=user, following=following).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({
                'errors':
                f'Вы не подписаны на пользователя {following.username}.'
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)
