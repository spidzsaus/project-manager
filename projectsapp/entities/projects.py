from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from dataclasses import dataclass
from uuid import UUID

from projectsapp.entities import IDComparable

if TYPE_CHECKING:
    from projectsapp.repo import Repo
    from projectsapp.entities.tasks import Task
    from projectsapp.entities.users import User


@dataclass(eq=False)
class Project(IDComparable):
    """
    Сущность проекта

    :param id: идентификатор проекта
    :param name: название проекта
    :param repo: репозиторий
    """

    id: UUID
    name: str
    repo: Repo

    def get_tasks(self) -> Iterable[Task]:
        """
        Возвращает задачи, которые принадлежат данному проекту.
        :return: задачи
        """

        return self.repo.get_tasks_for_project(self)

    def get_users(self) -> Iterable[User]:
        """
        Возвращает пользователей, которые состоят в данном проекте.
        :return: пользователи
        """

        return self.repo.get_users_for_project(self)

    def add_user(self, user: User):
        """
        Добавляет пользователя в проект.
        :param user: пользователь
        :return: пользователь
        """

        return self.repo.add_user_to_project(user, self)
