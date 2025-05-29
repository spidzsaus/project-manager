from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable
from uuid import UUID, uuid4

from projectsapp.entities import IDComparable

if TYPE_CHECKING:
    from projectsapp.entities.projects import Project
    from projectsapp.entities.users import User
    from projectsapp.entities.visitors import Visitor
    from projectsapp.entities.tasks import Task
    from projectsapp.repo import Repo


@dataclass(eq=False)
class TaskCategory(IDComparable):
    name: str
    project: Project
    repo: Repo
    description: str = ""
    id: UUID = field(default_factory=uuid4)

    def accept_visitor(self, visitor: Visitor):
        return visitor.visit_task_category(self)

    def get_users(self) -> Iterable[User]:
        return self.repo.get_users_for_task_category(self)

    def get_tasks(self) -> Iterable[Task]:
        return self.repo.get_tasks_in_task_category(self)

    def update_details(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
        self.repo.update_task_category(self)

    def add_user(self, user: User):
        self.repo.add_user_to_task_category(user, self)

    def remove_user(self, user: User):
        self.repo.remove_user_from_task_category(user, self)

    def add_task(self, task: Task):
        self.repo.add_task_to_task_category(task, self)

    def remove_task(self, task: Task):
        self.repo.remove_task_from_task_category(task, self)
