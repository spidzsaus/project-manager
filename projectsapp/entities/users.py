from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from dataclasses import dataclass
from uuid import UUID

from projectsapp.entities import IDComparable

if TYPE_CHECKING:
    from projectsapp.repo import Repo
    from projectsapp.entities.tasks import Task
    from projectsapp.entities.projects import Project


@dataclass(eq=False)
class User(IDComparable):
    """
    Сущность пользователя.

    :param id: уникальный идентификатор пользователя
    :param name: имя пользователя
    :param repo: репозиторий
    """

    id: UUID
    name: str
    repo: Repo

    def get_projects(self) -> Iterable[Project]:
        """
        Возвращает проекты, в которых участвует данный пользователь.
        :return: проекты
        """

        return self.repo.get_projects_for_user(self)

    def get_tasks(self, project: Project = None) -> Iterable[Task]:
        """
        Возвращает задачи, которые назначены данному пользователю.

        :param project: проект, в рамках которого нужно получить задачи (опционально)
        :return: задачи
        """

        return self.repo.get_tasks_for_user(self, project=project)
