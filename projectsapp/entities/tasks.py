from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime

from projectsapp.entities import IDComparable
from projectsapp.entities.records import JournalRecord

if TYPE_CHECKING:
    from projectsapp.repo import Repo
    from projectsapp.entities.projects import Project
    from projectsapp.entities.users import User
    from projectsapp.entities.visitors import Visitor


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
    description: str
    parent_project: Project
    
    end_date: datetime

    repo: Repo

    status: Status = Status.TODO
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
            record = JournalRecord(user=user, task=self, project=self.parent_project, event_type=JournalRecord.EventType.ASSIGN_TASK_TO_USER, repo=self.repo)
            self.repo.insert_journal_record(record)

        return self.repo.assign_task_to_user(user, self)

    def unassign_user(self, user: User, do_not_record: bool = False):
        """
        Удаляет назначение задачи пользователю.

        :param user: пользователь
        :param do_not_record: не записывать в журнал
        """

        if not do_not_record:
            record = JournalRecord(user=user, task=self, project=self.parent_project, event_type=JournalRecord.EventType.UNASSIGN_TASK_FROM_USER, repo=self.repo)
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

            record = JournalRecord(user=None, task=self, project=self.parent_project, event_type=event_type, repo=self.repo)
            self.repo.insert_journal_record(record)

        self.status = status
        self.repo.update_task(self)

    def accept_visitor(self, visitor: Visitor):
        return visitor.visit_task(self)