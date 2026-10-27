from rest_framework.permissions import BasePermission

class CanCreateProduct(BasePermission):
    """
    Permite cadastrar produtos apenas a operadores,
    administradores e superusuários.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True


        return user.groups.filter(
            name__in=["Operadores", "Administradores"]
        ).exists()