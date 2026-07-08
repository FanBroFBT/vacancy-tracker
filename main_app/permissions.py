from rest_framework import permissions


class IsEmployerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'employer'
            and hasattr(request.user, 'company')
        )


class IsVacancyOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.company.owner_id == request.user.id


class IsVacancyOwnerForStatusUpdate(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.vacancy.company.owner_id == request.user.id