from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Iterable
from uuid import UUID, uuid4

from projectsapp.entities import IDComparable
from projectsapp.entities.records import JournalRecord

if TYPE_CHECKING:
    from projectsapp.entities.projects import Project
    from projectsapp.entities.users import User
    from projectsapp.entities.visitors import Visitor
    from projectsapp.repo import Repo


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

    repo: Repo

    status: Status = Status.TODO
    description: str | None = None
    end_date: datetime | None = None
    id: UUID = field(default_factory=uuid4)

    def get_users(self) -> Iterable[User]:
        """
        Возвращает пользователей, которые назначены на данную задачу.

        :return: пользователи
        """

        return self.repo.get_users_for_task(self)

    def assign_user(self, user: User, do_not_record: bool = False):
        """
        Назначает задачу пользователю.

        :param user: пользователь
        :param do_not_record: не записывать в журнал
        """

        if not do_not_record:
            record = JournalRecord(
                user=user,
                task=self,
                project=self.parent_project,
                event_type=JournalRecord.EventType.ASSIGN_TASK_TO_USER,
                repo=self.repo,
            )
            self.repo.insert_journal_record(record)

        return self.repo.assign_task_to_user(user, self)

    def unassign_user(self, user: User, do_not_record: bool = False):
        """
        Удаляет назначение задачи пользователю.

        :param user: пользователь
        :param do_not_record: не записывать в журнал
        """

        if not do_not_record:
            record = JournalRecord(
                user=user,
                task=self,
                project=self.parent_project,
                event_type=JournalRecord.EventType.UNASSIGN_TASK_FROM_USER,
                repo=self.repo,
            )
            self.repo.insert_journal_record(record)

        return self.repo.unassign_user_from_task(user, self)

    def change_status(self, status: Status, do_not_record: bool = False):
        """
        Изменяет статус задачи.

        :param status: статус
        :param do_not_record: не записывать в журнал
        """

        if status == self.status:
            return

        if not do_not_record:
            match status:
                case Task.Status.TODO:
                    event_type = JournalRecord.EventType.SET_TODO
                case Task.Status.IN_PROCESS:
                    event_type = JournalRecord.EventType.SET_IN_PROCESS
                case Task.Status.DONE:
                    event_type = JournalRecord.EventType.SET_DONE

            record = JournalRecord(
                user=None,
                task=self,
                project=self.parent_project,
                event_type=event_type,
                repo=self.repo,
            )
            self.repo.insert_journal_record(record)

        self.status = status
        self.repo.update_task(self)

    def accept_visitor(self, visitor: Visitor):
        return visitor.visit_task(self)

    def get_tasks_dependent_on(self) -> Iterable[Task]:
        return self.repo.get_tasks_dependent_on_task(self)

    def get_dependency_tasks(self) -> Iterable[Task]:
        return self.repo.get_dependency_tasks_for_task(self)

    def add_dependency(self, dependency: Task):
        if dependency == self:
            return
        for task in dependency.dependency_dfs_backwards():
            if task == self:
                return
        self.repo.add_task_dependency(self, dependency)

    def remove_dependency(self, dependency: Task):
        self.repo.remove_task_dependency(self, dependency)

    def update_details(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
        self.repo.update_task(self)

    def blocked_by(self) -> Iterable[Task]:
        blockers = set()
        for task in self.get_dependency_tasks():
            if task.blocked_by() or task.status != Task.Status.DONE:
                blockers.add(task)
        return blockers

    def blocks_tasks(self) -> Iterable[Task]:
        return self.repo.get_tasks_dependent_on_task(self)

    def is_complete(self, lazy=True) -> bool:
        if lazy:
            return self.status == Task.Status.DONE
        return not self.blocked_by() and self.status == Task.Status.DONE

    def assigned_at(self) -> datetime:
        return datetime.now()  # Заглушка, так как нет информации о времени назначения

    def started_at(self) -> datetime:
        return datetime.now()  # Заглушка, так как нет информации о времени начала

    def done_at(self) -> datetime:
        return datetime.now()  # Заглушка, так как нет информации о времени завершения

    def dependency_dfs_backwards(self, visited=None):
        if visited is None:
            visited = set()
        visited.add(self)
        print(self.name)
        yield self
        for task in self.get_dependency_tasks():
            if task not in visited:
                yield from task.dependency_dfs_backwards(visited)
