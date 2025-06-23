from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class to allow access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsVendorUser(permissions.BasePermission):
    """
    Permission class to allow access only to vendor users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_vendor


class IsCustomerUser(permissions.BasePermission):
    """
    Permission class to allow access only to customer users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_customer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class to allow access to object owner or admin users.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is admin
        if request.user.is_admin:
            return True

        # Check if the user is the owner of the object
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # If object is the user itself
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id

        return False


class IsVendorOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class for vendor-specific objects.
    Allows access to vendor who owns the object or admin users.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is admin
        if request.user.is_admin:
            return True

        # Check if the user is a vendor and owns the object
        if request.user.is_vendor and hasattr(obj, 'vendor'):
            return obj.vendor == request.user

        return False


class IsAdminOrVendorReadOnly(permissions.BasePermission):
    """
    Permission class that allows admin full access and vendors read-only access.
    """
    def has_permission(self, request, view):
        if request.user.is_admin:
            return True

        if request.user.is_vendor and request.method in permissions.SAFE_METHODS:
            return True

        return False
