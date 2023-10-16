from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    The request is Admin as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )

class StaffUpdatePermission(BasePermission):
    """
    Custom permission to only staff user to update edit it.
    """
    def has_object_permission(self, request, view, obj):
        if (request.method == 'PUT' or request.method == 'PATCH') and not request.user.is_staff:
            return False
        return True

class AllowUnauthenticatedForCart(BasePermission):
    """
    Custom user permission to only authinticate user can perform merge_carts action.
    """
    def has_permission(self, request, view):
        if view.action == 'merge_carts':
            return request.user and request.user.is_authenticated
        return True
