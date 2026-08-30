from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Notification

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 'avatar')
        read_only_fields = ('id', 'email')



class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'actor', 'verb', 'target_url', 'is_read', 'created_at')
        read_only_fields = ('id', 'actor', 'verb', 'target_url', 'created_at')


class MessageResponseSerializer(serializers.Serializer):
    """
    Documents the small, non-model JSON bodies returned by custom actions
    (e.g. {"status": "..."}, {"message": "..."}, {"error": "..."}).
    Used only for OpenAPI schema generation via @extend_schema -- it is
    never actually instantiated/validated in a view.
    """
    status = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)