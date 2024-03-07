from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff
