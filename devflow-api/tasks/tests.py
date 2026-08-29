from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Membership, Project
from tasks.models import Task

User = get_user_model()


class TaskAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123', email='owner@example.com')
        self.member = User.objects.create_user(username='member', password='password123', email='member@example.com')
        
        self.project = Project.objects.create(name='DevFlow Tasks', owner=self.owner)
        Membership.objects.create(user=self.owner, project=self.project, role=Membership.Role.OWNER)
        Membership.objects.create(user=self.member, project=self.project, role=Membership.Role.MEMBER)

        self.task = Task.objects.create(
            title='Build Auth API',
            project=self.project,
            created_by=self.owner,
            assigned_to=self.member
        )

    def test_assigned_member_can_complete_task(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(f'/api/tasks/{self.task.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.COMPLETED)
