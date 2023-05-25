from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    """Права доступа, позволяющие редактировать объект либо его автору,
    либо суперюзеру."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or obj.author == request.user)
