from rest_framework import permissions

from projects.models import Membership


class IsTaskProjectMemberOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check user's role in the task's project
        membership = Membership.objects.filter(project=obj.project, user=request.user).first()
        if not membership:
            return False

        # Read permissions allowed to any project member
        if request.method in permissions.SAFE_METHODS:
            return True

        # Project owner has full permissions
        if membership.role == Membership.Role.OWNER:
            return True

        # Assignee can update or execute actions on their own task
        return obj.assigned_to == request.user and (request.method in ['PUT', 'PATCH'] or view.action in ['complete_task', 'archive_task'])