from rest_framework import permissions

from projects.models import Membership


class IsTaskProjectMemberOrOwner(permissions.BasePermission):
    """
    - Project owner: full access to every task in the project.
    - Assignee (not owner): may hit the complete/archive actions, and may
      PATCH only the whitelisted fields below on a task assigned to them.
      They can never PUT (full replace) a task, and can never touch fields
      like `project` or `assigned_to` themselves -- that would let an
      assignee re-scope or reassign a task they don't own.
    - Everyone else with read access: SAFE_METHODS only.
    - Non-members: no access at all.
    """

    # Fields a plain assignee is allowed to change via PATCH.
    ASSIGNEE_EDITABLE_FIELDS = frozenset({'status'})

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

        is_assignee = obj.assigned_to == request.user
        if not is_assignee:
            return False

        # Custom actions are already scoped to safe, single-purpose changes.
        if view.action in ['complete_task', 'archive_task']:
            return True

        # Otherwise, only allow a narrow PATCH -- never PUT, and never a
        # PATCH that touches fields outside the assignee's whitelist.
        if request.method == 'PATCH':
            submitted_fields = set(request.data.keys())
            return submitted_fields.issubset(self.ASSIGNEE_EDITABLE_FIELDS)

        return False


class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    """
    Any project member can read (list/retrieve) a comment -- that's already
    enforced by the queryset in CommentViewSet. Only the comment's own
    author can update or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user