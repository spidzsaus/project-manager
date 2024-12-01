from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime

from projectsapp.entities import IDComparable

if TYPE_CHECKING:
    from projectsapp.repo import Repo
    from projectsapp.entities.projects import Project
    from projectsapp.entities.users import User


@dataclass(eq=False)
class Task(IDComparable):
    """
    Сущность задачи.

    :param id: уникальный идентификатор задачи
    :param name: название задачи
    :param parent_project: проект, к которому принадлежит задача
    :param status: статус завершённости задачи
    :param end_date: срок выполнения задачи
    """

    class Status(Enum):
        """
        Статус завершённости задачи.
        """

        TODO = 0
        IN_PROCESS = 1
        DONE = 2

    name: str
    parent_project: Project
    status: Status
    end_date: datetime

    repo: Repo

    id: UUID = field(default_factory=uuid4)

    def get_users(self) -> Iterable[User]:
        """
        Возвращает пользователей, которые назначены на данную задачу.

        :return: пользователи
        """

        return self.repo.get_users_for_task(self)

    def assign_user(self, user: User):
        """
        Назначает задачу пользователю.

        :param user: пользователь
        """

        return self.repo.assign_task_to_user(user, self)

    def unassign_user(self, user: User):
        """
        Удаляет назначение задачи пользователю.

        :param user: пользователь
        """

        return self.repo.unassign_user_from_task(user, self)
