from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Membership, Project

User = get_user_model()


class ProjectAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123', email='owner@example.com')
        self.member = User.objects.create_user(username='member', password='password123', email='member@example.com')
        self.outsider = User.objects.create_user(username='outsider', password='password123', email='outsider@example.com')

        self.project = Project.objects.create(name='DevFlow Project', owner=self.owner)
        Membership.objects.create(user=self.owner, project=self.project, role=Membership.Role.OWNER)
        Membership.objects.create(user=self.member, project=self.project, role=Membership.Role.MEMBER)

    def test_owner_can_access_project(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_can_view_project(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outsider_cannot_access_project(self):
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_cannot_delete_project(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.delete(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)