from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Читать может любой аутентифицированный пользователь,
    редактировать/удалять — только автор объекта."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, "posted_by", None) or getattr(obj, "applicant", None)
        return owner == request.user