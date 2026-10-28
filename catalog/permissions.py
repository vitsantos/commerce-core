from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanCreateProduct(BasePermission):
    """
    Permite cadastrar produtos: operadores, administradores e superusuários.
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


class ProductPermission(BasePermission):
    """Controla a consulta, edição e exclusão de produtos."""
    def is_administrator(self, user):
        return user.is_superuser or user.groups.filter(
            name="Administradores"
        ).exists()


    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if self.is_administrator(user):
            return True

        if view.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return user.groups.filter(name="Operadores").exists()

        return False


    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if self.is_administrator(user):
            return True

        if view.action in ["update", "partial_update"]:
            return obj.created_by_id == user.id

        return False