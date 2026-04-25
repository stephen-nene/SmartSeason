# profiles/permissions.py
from rest_framework.permissions import BasePermission
from .models import UserRole

class CanManageSeason(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.can_manage_season(obj)


class IsAdmin(BasePermission):
    """Permission for admin users only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsAdminOrCoordinator(BasePermission):
    """Permission for admin or coordinator users"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.role in [UserRole.ADMIN, UserRole.COORDINATOR]


class IsOwnerOrAdmin(BasePermission):
    """Permission for object owner or admin"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN:
            return True
        return obj.id == request.user.id


class IsFieldAssignmentCreatorOrAdmin(BasePermission):
    """Permission for field assignment"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN:
            return True
        return obj.assigned_by == request.user
