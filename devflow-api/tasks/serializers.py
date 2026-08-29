from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Comment, Task


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'content', 'created_at')
        read_only_fields = ('id', 'author', 'created_at')


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'priority',
            'project', 'assigned_to', 'assigned_to_detail',
            'created_by', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_project(self, value):
        user = self.context['request'].user
        if not value.members.filter(id=user.id).exists():
            raise serializers.ValidationError("You can only create tasks for projects you belong to.")
        return value