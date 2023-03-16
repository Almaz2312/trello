from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_member = obj.members.filter(member=request.user).exists()
        if request.method in SAFE_METHODS:
            return obj.owner == request.user or is_member
        return obj.owner == request.user

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_member = obj.members.filter(member=request.user).exists()
        return obj.owner == request.user or is_member

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
