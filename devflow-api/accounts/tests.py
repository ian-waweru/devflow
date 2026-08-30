from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Notification
from projects.models import Membership, Project

User = get_user_model()


class AuthAPITests(APITestCase):
    def test_user_can_register(self):
        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'strongpassword123',
            'first_name': 'New',
            'last_name': 'User',
        }
        response = self.client.post('/api/auth/register/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Password must never come back in the response.
        self.assertNotIn('password', response.data)

    def test_register_missing_required_field_returns_400(self):
        payload = {'username': 'incomplete', 'password': 'strongpassword123'}
        response = self.client.post('/api/auth/register/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='incomplete').exists())

    def test_register_short_password_returns_400(self):
        payload = {
            'username': 'shortpw',
            'email': 'shortpw@example.com',
            'password': '123',
        }
        response = self.client.post('/api/auth/register/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='shortpw').exists())

    def test_register_duplicate_username_returns_400(self):
        User.objects.create_user(username='taken', password='password123', email='taken@example.com')
        payload = {
            'username': 'taken',
            'email': 'different@example.com',
            'password': 'strongpassword123',
        }
        response = self.client.post('/api/auth/register/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email_returns_400(self):
        User.objects.create_user(username='original', password='password123', email='dupe@example.com')
        payload = {
            'username': 'different',
            'email': 'dupe@example.com',
            'password': 'strongpassword123',
        }
        response = self.client.post('/api/auth/register/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITests(APITestCase):
    def setUp(self):
        self.password = 'strongpassword123'
        self.user = User.objects.create_user(
            username='loginuser', password=self.password, email='loginuser@example.com'
        )

    def test_user_can_login_with_correct_credentials(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'loginuser', 'password': self.password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_wrong_password_returns_401(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'loginuser', 'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_nonexistent_user_returns_401(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'ghost', 'password': 'whatever123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_token_can_be_refreshed(self):
        login_response = self.client.post('/api/auth/login/', {
            'username': 'loginuser', 'password': self.password
        })
        refresh_token = login_response.data['refresh']
        response = self.client.post('/api/auth/token/refresh/', {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class MeEndpointAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser', password='password123', email='profileuser@example.com'
        )

    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_fetch_own_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')

    def test_authenticated_user_can_update_bio(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/api/auth/me/', {'bio': 'Backend developer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, 'Backend developer')

    def test_email_field_is_read_only_on_update(self):
        """Email is listed as read_only in UserSerializer -- confirm it can't be changed via /me/."""
        original_email = self.user.email
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/api/auth/me/', {'email': 'hacked@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email)


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

    def test_filter_notifications_by_is_read(self):
        Notification.objects.create(recipient=self.assignee, actor=self.owner, verb="Unread alert")
        Notification.objects.create(recipient=self.assignee, actor=self.owner, verb="Read alert", is_read=True)

        self.client.force_authenticate(user=self.assignee)
        response = self.client.get('/api/auth/notifications/?is_read=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verbs = {n['verb'] for n in response.data['results']}
        self.assertEqual(verbs, {'Unread alert'})