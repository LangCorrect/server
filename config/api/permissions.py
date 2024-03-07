from rest_framework import permissions

from langcorrect.posts.models import PostVisibility


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class CanViewPost(permissions.BasePermission):
    message = "You do not have permission to view this post."

    def has_object_permission(self, request, view, obj):
        if (
            obj.permission == PostVisibility.PUBLIC
            or obj.permission == PostVisibility.MEMBER
            and request.user.is_authenticated
        ):
            return True
        else:
            return False
