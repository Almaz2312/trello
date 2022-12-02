from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        is_member = obj.members.filter(member=user).exists()
        return obj.owner == user or is_member
