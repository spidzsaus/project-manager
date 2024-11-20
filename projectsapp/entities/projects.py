from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from dataclasses import dataclass
from uuid import UUID

if TYPE_CHECKING:
    from projectsapp.repo import Repo
    from projectsapp.entities.tasks import Task
    from projectsapp.entities.users import User

@dataclass
class Project:
    id: UUID
    name: str
    repo: Repo

    def get_tasks(self) -> Iterable[Task]:
        return self.repo.get_tasks_for_project(self)
    
    def get_users(self) -> Iterable[User]:
        return self.repo.get_users_for_project(self)