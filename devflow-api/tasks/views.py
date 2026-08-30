from typing import ClassVar

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Notification
from projects.models import ActivityLog

from .models import Comment, Task
from .permissions import IsCommentAuthorOrReadOnly, IsTaskProjectMemberOrOwner
from .serializers import CommentSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes: ClassVar[list] = [IsAuthenticated, IsTaskProjectMemberOrOwner]
    filterset_fields: ClassVar[list[str]] = ['status', 'priority', 'project', 'assigned_to']
    search_fields: ClassVar[list[str]] = ['title', 'description']
    ordering_fields: ClassVar[list[str]] = ['priority', 'created_at', 'updated_at']

    def get_queryset(self):
        # Prevent schema generation crash when evaluated with AnonymousUser
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Task.objects.none()

        # Users only see tasks from projects they belong to
        return (
            Task.objects.filter(project__members=self.request.user)
            .select_related('project', 'assigned_to', 'created_by')
            .distinct()
        )

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        ActivityLog.objects.create(
            project=task.project,
            user=self.request.user,
            action=f"Created task '{task.title}'"
        )
        # 2. Trigger Notification if assigned to another user
        if task.assigned_to and task.assigned_to != self.request.user:
            Notification.objects.create(
                recipient=task.assigned_to,
                actor=self.request.user,
                verb=f"assigned you to task '{task.title}'",
                target_url=f"/api/tasks/{task.id}/"
            )

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_task(self, request, pk=None):
        task = self.get_object()
        task.status = Task.Status.COMPLETED
        task.save()
        
        ActivityLog.objects.create(
            project=task.project,
            user=request.user,
            action=f"Marked task '{task.title}' as COMPLETED"
        )
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='archive')
    def archive_task(self, request, pk=None):
        task = self.get_object()
        task.status = Task.Status.ARCHIVED
        task.save()

        ActivityLog.objects.create(
            project=task.project,
            user=request.user,
            action=f"Archived task '{task.title}'"
        )
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes: ClassVar[list] = [IsAuthenticated, IsCommentAuthorOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(task__project__members=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)