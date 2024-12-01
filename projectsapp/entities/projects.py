from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from dataclasses import dataclass, field
from uuid import UUID, uuid4

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

    name: str
    repo: Repo
    id: UUID = field(default_factory=uuid4)

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

    def promote_user(self, user: User):
        """
        Повышает пользователя в роли администратора в проекте.
        Если пользователь не состоит в проекте, то ничего не делает.
        :param user: пользователь
        :return: пользователь
        """

        return self.repo.promote_user_in_project(user, self)
    
    def add_owner(self, user: User):
        """
        Добавляет владельца проекта в проект.
        То же самое, что и add_user, но пользователь сразу
        получает права администратора.
        :param user: владелец проекта
        """

        return self.repo.add_owner_to_project(user, self)