from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from dataclasses import dataclass
from uuid import UUID

if TYPE_CHECKING:
    from projectsapp.repo import Repo
    from projectsapp.entities.tasks import Task
    from projectsapp.entities.projects import Project

@dataclass
class User:
    id: UUID
    name: str
    repo: Repo

    def get_projects(self) -> Iterable[Project]:
        return self.repo.get_projects_for_user(self)

    def get_tasks(self, project: Project = None) -> Iterable[Task]:
        return self.repo.get_tasks_for_user(self, project=project)