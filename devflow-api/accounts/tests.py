from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Notification
from projects.models import Membership, Project

User = get_user_model()


class NotificationAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner', password='password123', email='owner@example.com'
        )
        self.assignee = User.objects.create_user(
            username='assignee', password='password123', email='assignee@example.com'
        )
        self.outsider = User.objects.create_user(
            username='outsider', password='password123', email='outsider@example.com'
        )

        self.project = Project.objects.create(name='DevFlow App', owner=self.owner)
        Membership.objects.create(user=self.owner, project=self.project, role=Membership.Role.OWNER)
        Membership.objects.create(user=self.assignee, project=self.project, role=Membership.Role.MEMBER)

    def test_task_assignment_triggers_notification(self):
        self.client.force_authenticate(user=self.owner)
        payload = {
            'title': 'Implement Notifications',
            'description': 'Build unit tests for alerts',
            'project': self.project.id,
            'assigned_to': self.assignee.id,
        }
        response = self.client.post('/api/tasks/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check notification creation for assignee
        notification = Notification.objects.filter(recipient=self.assignee).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.actor, self.owner)
        self.assertIn("assigned you to task", notification.verb)

    def test_user_can_fetch_own_notifications(self):
        Notification.objects.create(
            recipient=self.assignee,
            actor=self.owner,
            verb="added you to project 'DevFlow App'"
        )

        self.client.force_authenticate(user=self.assignee)
        response = self.client.get('/api/auth/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_user_cannot_access_other_user_notifications(self):
        Notification.objects.create(
            recipient=self.assignee,
            actor=self.owner,
            verb="added you to project 'DevFlow App'"
        )

        self.client.force_authenticate(user=self.outsider)
        response = self.client.get('/api/auth/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_mark_single_notification_as_read(self):
        notification = Notification.objects.create(
            recipient=self.assignee,
            actor=self.owner,
            verb="assigned you to a task"
        )

        self.client.force_authenticate(user=self.assignee)
        response = self.client.post(f'/api/auth/notifications/{notification.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_notifications_as_read(self):
        Notification.objects.create(recipient=self.assignee, actor=self.owner, verb="Alert 1")
        Notification.objects.create(recipient=self.assignee, actor=self.owner, verb="Alert 2")

        self.client.force_authenticate(user=self.assignee)
        response = self.client.post('/api/auth/notifications/read-all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        unread_count = Notification.objects.filter(recipient=self.assignee, is_read=False).count()
        self.assertEqual(unread_count, 0)