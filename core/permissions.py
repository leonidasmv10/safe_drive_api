from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite lectura a cualquiera autenticado, escritura solo a admins.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff
