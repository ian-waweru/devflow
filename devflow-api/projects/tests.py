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

    def test_unauthenticated_user_cannot_list_projects(self):
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_project(self):
        response = self.client.post('/api/projects/', {'name': 'Should Fail'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_missing_name_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/projects/', {'description': 'No name given'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creating_project_auto_assigns_creator_as_owner_membership(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/projects/', {'name': 'Brand New Project'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_project = Project.objects.get(id=response.data['id'])
        membership = Membership.objects.get(project=new_project, user=self.owner)
        self.assertEqual(membership.role, Membership.Role.OWNER)


class MembershipAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='m_owner', password='password123', email='m_owner@example.com')
        self.member = User.objects.create_user(username='m_member', password='password123', email='m_member@example.com')
        self.newcomer = User.objects.create_user(
            username='newcomer', password='password123', email='newcomer@example.com'
        )

        self.project = Project.objects.create(name='Membership Project', owner=self.owner)
        Membership.objects.create(user=self.owner, project=self.project, role=Membership.Role.OWNER)
        Membership.objects.create(user=self.member, project=self.project, role=Membership.Role.MEMBER)

    def test_owner_can_add_member(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f'/api/projects/{self.project.id}/add-member/', {'username': 'newcomer'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Membership.objects.filter(project=self.project, user=self.newcomer).exists()
        )

    def test_member_cannot_add_member(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            f'/api/projects/{self.project.id}/add-member/', {'username': 'newcomer'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            Membership.objects.filter(project=self.project, user=self.newcomer).exists()
        )

    def test_add_member_with_unknown_username_returns_404(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f'/api/projects/{self.project.id}/add-member/', {'username': 'doesnotexist'}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_member_missing_username_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/add-member/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_remove_member(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f'/api/projects/{self.project.id}/remove-member/', {'username': 'm_member'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Membership.objects.filter(project=self.project, user=self.member).exists()
        )

    def test_owner_cannot_remove_project_owner(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f'/api/projects/{self.project.id}/remove-member/', {'username': 'm_owner'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            Membership.objects.filter(project=self.project, user=self.owner).exists()
        )

    def test_member_cannot_remove_another_member(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            f'/api/projects/{self.project.id}/remove-member/', {'username': 'm_owner'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)