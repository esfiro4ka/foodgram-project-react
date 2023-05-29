from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class IsAuthorOrAdmin(IsAuthenticatedOrReadOnly):
    """Права доступа, позволяющие редактировать объект либо его автору,
    либо суперюзеру."""

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_superuser
                or obj.author == request.user)
