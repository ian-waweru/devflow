from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Membership, Project
from tasks.models import Comment, Task

User = get_user_model()


class TaskAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123', email='owner@example.com')
        self.member = User.objects.create_user(username='member', password='password123', email='member@example.com')
        self.other_member = User.objects.create_user(
            username='other_member', password='password123', email='other_member@example.com'
        )

        self.project = Project.objects.create(name='DevFlow Tasks', owner=self.owner)
        Membership.objects.create(user=self.owner, project=self.project, role=Membership.Role.OWNER)
        Membership.objects.create(user=self.member, project=self.project, role=Membership.Role.MEMBER)
        Membership.objects.create(user=self.other_member, project=self.project, role=Membership.Role.MEMBER)

        self.other_project = Project.objects.create(name='Other Project', owner=self.owner)
        Membership.objects.create(user=self.owner, project=self.other_project, role=Membership.Role.OWNER)

        # A project self.owner has no membership in at all -- used to test
        # that you can't create a task in a project you don't belong to.
        self.stranger = User.objects.create_user(
            username='stranger', password='password123', email='stranger@example.com'
        )
        self.foreign_project = Project.objects.create(name='Foreign Project', owner=self.stranger)
        Membership.objects.create(user=self.stranger, project=self.foreign_project, role=Membership.Role.OWNER)

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

    def test_assignee_can_patch_status_only(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(f'/api/tasks/{self.task.id}/', {'status': Task.Status.IN_PROGRESS})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.IN_PROGRESS)

    def test_assignee_cannot_reassign_task_via_patch(self):
        """An assignee must not be able to hand the task to someone else."""
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(
            f'/api/tasks/{self.task.id}/', {'assigned_to': self.other_member.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.task.refresh_from_db()
        self.assertEqual(self.task.assigned_to, self.member)

    def test_assignee_cannot_move_task_to_another_project_via_patch(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(
            f'/api/tasks/{self.task.id}/', {'project': self.other_project.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.task.refresh_from_db()
        self.assertEqual(self.task.project, self.project)

    def test_assignee_cannot_put_task(self):
        """PUT (full replace) should be blocked for assignees entirely."""
        self.client.force_authenticate(user=self.member)
        response = self.client.put(f'/api/tasks/{self.task.id}/', {
            'title': 'Hijacked title',
            'status': Task.Status.IN_PROGRESS,
            'priority': Task.Priority.LOW,
            'project': self.project.id,
            'assigned_to': self.member.id,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_still_fully_update_task(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f'/api/tasks/{self.task.id}/', {'assigned_to': self.other_member.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.assigned_to, self.other_member)

    def test_non_assignee_member_cannot_patch_task(self):
        self.client.force_authenticate(user=self.other_member)
        response = self.client.patch(
            f'/api/tasks/{self.task.id}/', {'status': Task.Status.IN_PROGRESS}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_list_tasks(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_create_task(self):
        response = self.client.post('/api/tasks/', {'title': 'Nope', 'project': self.project.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_missing_title_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/tasks/', {'project': self.project.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_missing_project_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/tasks/', {'title': 'No project given'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_for_foreign_project_returns_400(self):
        """validate_project() should reject tasks for a project you don't belong to."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/tasks/', {
            'title': 'Sneaky task', 'project': self.foreign_project.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_with_invalid_status_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/tasks/', {
            'title': 'Bad status', 'project': self.project.id, 'status': 'not_a_real_status'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='c_owner', password='password123', email='c_owner@example.com')
        self.author = User.objects.create_user(username='c_author', password='password123', email='c_author@example.com')
        self.other_member = User.objects.create_user(
            username='c_other', password='password123', email='c_other@example.com'
        )

        self.project = Project.objects.create(name='Comment Project', owner=self.owner)
        Membership.objects.create(user=self.owner, project=self.project, role=Membership.Role.OWNER)
        Membership.objects.create(user=self.author, project=self.project, role=Membership.Role.MEMBER)
        Membership.objects.create(user=self.other_member, project=self.project, role=Membership.Role.MEMBER)

        self.task = Task.objects.create(
            title='Task with comments', project=self.project, created_by=self.owner
        )
        self.comment = Comment.objects.create(task=self.task, author=self.author, content='Original comment')

    def test_any_project_member_can_read_comment(self):
        self.client.force_authenticate(user=self.other_member)
        response = self.client.get(f'/api/tasks/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_can_edit_own_comment(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.patch(f'/api/tasks/comments/{self.comment.id}/', {'content': 'Edited'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Edited')

    def test_other_member_cannot_edit_someone_elses_comment(self):
        self.client.force_authenticate(user=self.other_member)
        response = self.client.patch(f'/api/tasks/comments/{self.comment.id}/', {'content': 'Hijacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Original comment')

    def test_other_member_cannot_delete_someone_elses_comment(self):
        self.client.force_authenticate(user=self.other_member)
        response = self.client.delete(f'/api/tasks/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_author_can_delete_own_comment(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.delete(f'/api/tasks/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())