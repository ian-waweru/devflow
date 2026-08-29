from rest_framework import permissions

from .models import Membership


class IsProjectMemberOrOwner(permissions.BasePermission):
    """
    Custom permission to ensure:
    - Owners have full access (GET, PUT, PATCH, DELETE).
    - Members have read-only access (GET).
    - Non-members have no access.
    """

    def has_object_permission(self, request, view, obj):
        # Check membership status in the project
        membership = Membership.objects.filter(project=obj, user=request.user).first()
        
        if not membership:
            return False

        # Read permissions are allowed to any project member
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the project owner
        return membership.role == Membership.Role.OWNER