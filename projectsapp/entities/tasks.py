from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from dataclasses import dataclass
from uuid import UUID
from enum import Enum
from datetime import datetime

from projectsapp.entities import IDComparable
if TYPE_CHECKING:
    from projectsapp.repo import Repo
    from projectsapp.entities.projects import Project
    from projectsapp.entities.users import User

@dataclass(eq=False)
class Task(IDComparable):
    class Status(Enum):
        TODO = 0
        IN_PROCESS = 1
        DONE = 2

    id: UUID
    name: str
    parent_project: Project
    status: Status
    end_date: datetime

    repo: Repo

    def get_users(self) -> Iterable[User]:
        return self.repo.get_users_for_task(self)

    def assign_user(self, user: User):
        return self.repo.assign_task_to_user(user, self)
    
    def unassign_user(self, user: User):
        return self.repo.unassign_user_from_task(user, self)
