from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. We extend AbstractUser (not AbstractBaseUser) so we
    keep Django's built-in username/password/auth machinery, and just add
    fields on top as we need them.
    """
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)

    def __str__(self):
        return self.username


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_notifications'
    )
    verb = models.CharField(max_length=255)  # e.g., "assigned you to task 'Build Auth API'"
    target_url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.verb}"