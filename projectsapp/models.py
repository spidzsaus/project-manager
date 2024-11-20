from __future__ import annotations
from typing import TYPE_CHECKING

from django.db import models

from projectsapp.entities.projects import Project
from projectsapp.entities.users import User
from projectsapp.entities.tasks import Task

if TYPE_CHECKING:
    from projectsapp.repo import Repo

class ProjectModel(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=128)
    # ...

    def as_entity(self, repo: Repo) -> Project:
        return Project(id=self.id, name=self.name, repo=repo)



class TaskModel(models.Model):
    class Status(models.IntegerChoices):
        TODO = 0
        IN_PROCESS = 1
        DONE = 2

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=128)
    parent_project = models.ForeignKey(ProjectModel, null=False, on_delete=models.CASCADE)
    status = models.IntegerField(choices=Status, default=Status.TODO)
    end_date = models.DateTimeField(null=True)
    # ...

    def as_entity(self, repo: Repo) -> Task:
        """Convert this model to an entity."""
        parent_project = self.parent_project.as_entity(repo)
        return Task(
            id=self.id,
            name=self.name,
            parent_project=parent_project,
            status=Task.Status(self.status),
            end_date=self.end_date,
            repo=repo,
        )
    


class UserModel(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=128)
    # ...

    def as_entity(self, repo: Repo) -> User:
        return User(id=self.id, name=self.name, repo=repo)
    


class MembershipModel(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(UserModel, null=False, on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectModel, null=False, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

class TaskAssignmentModel(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(UserModel, null=False, on_delete=models.CASCADE)
    task = models.ForeignKey(TaskModel, null=False, on_delete=models.CASCADE)