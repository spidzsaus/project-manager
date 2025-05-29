from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable
from uuid import UUID, uuid4

from projectsapp.entities import IDComparable
from projectsapp.entities.task_category import TaskCategory

if TYPE_CHECKING:
    from projectsapp.entities.projects import Project
    from projectsapp.entities.tasks import Task
    from projectsapp.entities.visitors import Visitor
    from projectsapp.repo import Repo


@dataclass(eq=False)
class User(IDComparable):
    """
    Сущность пользователя.

    :param id: уникальный идентификатор пользователя
    :param name: имя пользователя
    :param repo: репозиторий
    """

    name: str
    repo: Repo

    id: UUID = field(default_factory=uuid4)

    def get_projects(self) -> Iterable[Project]:
        """
        Возвращает проекты, в которых участвует данный пользователь.
        :return: проекты
        """

        return self.repo.get_projects_for_user(self)

    def get_tasks(
        self, project: Project | None = None, sort_by_status: bool = False
    ) -> Iterable[Task]:
        """
        Возвращает задачи, которые назначены данному пользователю.

        :param project: проект, в рамках которого нужно получить задачи (опционально)
        :param sort_by_status: сортировать ли задачи по статусу (опционально)
        :return: задачи
        """

        return self.repo.get_tasks_for_user(
            self, project=project, sort_by_status=sort_by_status
        )

    def is_admin_in_project(self, project: Project) -> bool:
        return self.repo.is_user_admin_in_project(self, project)

    def accept_visitor(self, visitor: Visitor) -> None:
        return visitor.visit_user(self)

    @property
    def is_authenticated(self) -> bool:
        return True  # TODO

    def get_task_categories(self) -> Iterable[TaskCategory]:
        return self.repo.get_task_categories_for_user(self)

    def is_suitable_for_task(self, task: Task) -> bool:
        # TODO maybe it can be rewritten using SQL queries

        task_categories = task.get_task_categories()
        user_categories = self.get_task_categories()

        for task_category in task_categories:
            if task_category not in user_categories:
                return False

        return True
