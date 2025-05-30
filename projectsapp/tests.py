import datetime
from uuid import UUID

from django.test import TestCase

from projectsapp.entities.projects import Project
from projectsapp.entities.tasks import Task
from projectsapp.entities.users import User
from projectsapp.repo import Repo

# Create your tests here.


class RepoTest(TestCase):
    def test_repo(self):
        repo = Repo()

        user = User(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            username="test_user",
            repo=repo,
        )
        project = Project(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="test_project",
            repo=repo,
        )
        task = Task(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="test_task",
            parent_project=project,
            status=Task.Status.TODO,
            end_date=datetime.datetime(
                year=2022, month=1, day=1, tzinfo=datetime.timezone.utc
            ),
            repo=repo,
        )
        repo.insert_project(project)
        repo.insert_user(user)
        repo.insert_task(task)

        repo.add_user_to_project(user, project)

        task.assign_user(user)

        self.assertSetEqual(set(task.get_users()), set([user]))
        self.assertSetEqual(set(project.get_users()), set([user]))
        self.assertSetEqual(set(user.get_tasks(project=project)), set([task]))
        self.assertSetEqual(set(user.get_projects()), set([project]))

        repo.remove_user_from_project(user, project)

        task.unassign_user(user)

        self.assertSetEqual(set(task.get_users()), set([]))
        self.assertSetEqual(set(project.get_users()), set([]))
        self.assertSetEqual(set(user.get_tasks(project=project)), set([]))
        self.assertSetEqual(set(user.get_projects()), set([]))
