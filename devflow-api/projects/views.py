from typing import ClassVar

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Notification
from accounts.serializers import MessageResponseSerializer

from .models import ActivityLog, Membership, Project
from .permissions import IsProjectMemberOrOwner
from .serializers import (
    ActivityLogSerializer,
    MembershipActionSerializer,
    MembershipSerializer,
    ProjectSerializer,
)

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes: ClassVar[list] = [IsAuthenticated, IsProjectMemberOrOwner]
    filterset_fields: ClassVar[list[str]] = ['owner']
    search_fields: ClassVar[list[str]] = ['name', 'description']
    ordering_fields: ClassVar[list[str]] = ['name', 'created_at', 'updated_at']

    def get_queryset(self):
        # Prevent schema generation crash when evaluated with AnonymousUser
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Project.objects.none()

        # Users only see projects where they are members or owners
        return (
            Project.objects.filter(members=self.request.user)
            .select_related('owner')
            .prefetch_related('members')
            .distinct()
        )

    @extend_schema(
        request=MembershipActionSerializer,
        responses={
            201: MembershipSerializer,
            400: MessageResponseSerializer,
            404: MessageResponseSerializer,
        },
    )
    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        project = self.get_object()
        username = request.data.get('username')

        if not username:
            return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_to_add = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        membership, created = Membership.objects.get_or_create(
            project=project,
            user=user_to_add,
            defaults={'role': Membership.Role.MEMBER}
        )

        if not created:
            return Response({'message': 'User is already a member.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Log Activity Feed Entry
        ActivityLog.objects.create(
            project=project,
            user=request.user,
            action=f"Added {user_to_add.username} to project '{project.name}'"
        )

        # 2. Trigger User Notification
        Notification.objects.create(
            recipient=user_to_add,
            actor=request.user,
            verb=f"added you to project '{project.name}'",
            target_url=f"/api/projects/{project.id}/"
        )

        return Response(MembershipSerializer(membership).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=MembershipActionSerializer,
        responses={
            200: MessageResponseSerializer,
            400: MessageResponseSerializer,
            404: MessageResponseSerializer,
        },
    )
    @action(detail=True, methods=['post'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        project = self.get_object()
        username = request.data.get('username')

        try:
            user_to_remove = User.objects.get(username=username)
            membership = Membership.objects.get(project=project, user=user_to_remove)
            
            if membership.role == Membership.Role.OWNER:
                return Response({'error': 'Cannot remove project owner.'}, status=status.HTTP_400_BAD_REQUEST)
                
            membership.delete()
            return Response({'message': 'Member removed successfully.'}, status=status.HTTP_200_OK)
        except (User.DoesNotExist, Membership.DoesNotExist):
            return Response({'error': 'Member not found in project.'}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        project = serializer.save()
        ActivityLog.objects.create(
            project=project,
            user=self.request.user,
            action=f"Created project '{project.name}'"
        )

    @extend_schema(responses=ActivityLogSerializer(many=True), filters=False)
    @action(detail=True, methods=['get'], url_path='activity')
    def activity(self, request, pk=None):
        project = self.get_object()
        activities = project.activities.all()
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = ActivityLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ActivityLogSerializer(activities, many=True)
        return Response(serializer.data)