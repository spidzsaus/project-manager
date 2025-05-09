from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models

from projectsapp.entities.projects import Project
from projectsapp.entities.records import JournalRecord
from projectsapp.entities.tasks import Task
from projectsapp.entities.users import User

if TYPE_CHECKING:
    from projectsapp.repo import Repo


class ProjectModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=128)
    # ...

    def as_entity(self, repo: Repo) -> Project:
        return Project(id=self.id, name=self.name, repo=repo)


class TaskModel(models.Model):
    class Status(models.IntegerChoices):
        TODO = 0
        IN_PROCESS = 1
        DONE = 2

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, default=None, blank=True)
    parent_project = models.ForeignKey(
        ProjectModel, null=False, on_delete=models.CASCADE
    )
    status = models.IntegerField(choices=Status.choices, default=Status.TODO)
    end_date = models.DateTimeField(null=True)
    # ...

    def as_entity(self, repo: Repo) -> Task:
        """Convert this model to an entity."""
        parent_project = self.parent_project.as_entity(repo)
        return Task(
            id=self.id,
            name=self.name,
            description=self.description,
            parent_project=parent_project,
            status=Task.Status(self.status),
            end_date=self.end_date,
            repo=repo,
        )


class TaskDependencyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    task = models.ForeignKey(
        TaskModel, null=False, on_delete=models.CASCADE, related_name="task"
    )
    depends_on = models.ForeignKey(
        TaskModel, null=False, on_delete=models.CASCADE, related_name="depends_on"
    )
    dependency_timestamp = models.DateTimeField(auto_now_add=True)


class UserModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=128)
    # ...

    def as_entity(self, repo: Repo) -> User:
        return User(id=self.id, name=self.name, repo=repo)


class MembershipModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(UserModel, null=False, on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectModel, null=False, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)


class TaskAssignmentModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(UserModel, null=False, on_delete=models.CASCADE)
    task = models.ForeignKey(TaskModel, null=False, on_delete=models.CASCADE)


class JournalRecordModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(UserModel, null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(TaskModel, null=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(ProjectModel, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)

    class EventType(models.IntegerChoices):
        ASSIGN_TASK_TO_USER = 0
        UNASSIGN_TASK_FROM_USER = 1
        SET_IN_PROCESS = 2
        SET_DONE = 3
        SET_TODO = 4
        ADD_USER_TO_PROJECT = 5
        PROMOTE_USER_IN_PROJECT = 6

    event_type = models.IntegerField(choices=EventType.choices)

    def as_entity(self, repo: Repo) -> JournalRecord:
        return JournalRecord(
            user=self.user and self.user.as_entity(repo),
            task=self.task and self.task.as_entity(repo),
            project=self.project and self.project.as_entity(repo),
            date=self.date,
            event_type=JournalRecord.EventType(self.event_type),
            repo=repo,
            id=self.id,
        )
