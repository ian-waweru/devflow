from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import ActivityLog, Membership, Project


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ('id', 'user', 'role', 'joined_at')


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'owner', 'members_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')

    @extend_schema_field(int)
    def get_members_count(self, obj):
        return obj.members.count()

    def create(self, validated_data):
        user = self.context['request'].user
        project = Project.objects.create(owner=user, **validated_data)
        # Automatically add creator as an Owner in Membership
        Membership.objects.create(user=user, project=project, role=Membership.Role.OWNER)
        return project



class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ActivityLog
        fields = ('id', 'project', 'user', 'action', 'timestamp')
        read_only_fields = ('id', 'project', 'user', 'action', 'timestamp')