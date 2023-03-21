from rest_framework import permissions


class AuthorOrReadOnlyPermission(permissions.BasePermission):
    """Ограничение доступа для неавторизованных
    пользователей, а также запрет на изменение контента
    других пользователей.
    """
    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user or
            request.user.is_superuser or
            request.method in permissions.SAFE_METHODS
        )
