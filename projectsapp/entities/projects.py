from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable
from uuid import UUID, uuid4

from projectsapp.entities import IDComparable
from projectsapp.entities.records import JournalRecord
from projectsapp.entities.task_category import TaskCategory

if TYPE_CHECKING:
    from projectsapp.entities.tasks import Task
    from projectsapp.entities.users import User
    from projectsapp.entities.visitors import Visitor
    from projectsapp.repo import Repo


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

    def get_journal_records(self) -> Iterable[JournalRecord]:
        """
        Возвращает записи журнала для данного проекта.
        :return: записи журнала
        """

        return self.repo.get_journal_records_for_project(self)

    def add_user(self, user: User, do_not_record: bool = False):
        """
        Добавляет пользователя в проект.
        :param user: пользователь
        :param do_not_record: не записывать в журнал
        :return: пользователь
        """

        if not do_not_record:
            record = JournalRecord(
                user=user,
                task=None,
                project=self,
                event_type=JournalRecord.EventType.ADD_USER_TO_PROJECT,
                repo=self.repo,
            )
            self.repo.insert_journal_record(record)

        return self.repo.add_user_to_project(user, self)

    def promote_user(self, user: User, do_not_record: bool = False):
        """
        Повышает пользователя в роли администратора в проекте.
        Если пользователь не состоит в проекте, то ничего не делает.
        :param user: пользователь
        :return: пользователь
        """

        if not do_not_record:
            record = JournalRecord(
                user=user,
                task=None,
                project=self,
                event_type=JournalRecord.EventType.PROMOTE_USER_IN_PROJECT,
                repo=self.repo,
            )
            self.repo.insert_journal_record(record)

        return self.repo.promote_user_in_project(user, self)

    def add_owner(self, user: User, do_not_record: bool = False):
        """
        Добавляет владельца проекта в проект.
        То же самое, что и add_user, но пользователь сразу
        получает права администратора.
        :param user: владелец проекта
        """

        if not do_not_record:
            record_1 = JournalRecord(
                user=user,
                task=None,
                project=self,
                event_type=JournalRecord.EventType.ADD_USER_TO_PROJECT,
                repo=self.repo,
            )
            record_2 = JournalRecord(
                user=user,
                task=None,
                project=self,
                event_type=JournalRecord.EventType.PROMOTE_USER_IN_PROJECT,
                repo=self.repo,
            )
            self.repo.insert_journal_record(record_1)
            self.repo.insert_journal_record(record_2)

        return self.repo.add_owner_to_project(user, self)

    def accept_visitor(self, visitor: Visitor) -> None:
        return visitor.visit_project(self)

    def calc_progress(self) -> float:
        tasks = self.repo.get_tasks_for_project(self)
        tasks_counter = complete_tasks_counter = 0
        for t in tasks:
            tasks_counter += 1
            if t.is_complete():
                complete_tasks_counter += 1

        return complete_tasks_counter / tasks_counter if tasks_counter else 0.0

    def get_tasks_for_user(self, user: User) -> Iterable[Task]:
        return self.repo.get_tasks_for_user(user, self)

    def get_task_categories(self) -> Iterable[TaskCategory]:
        return self.repo.get_task_categories_for_project(self)


class AutoTaskAssigner:

    def __init__(self, repo: Repo, project: Project):
        self.repo = repo
        self.project = project

    def auto_assign_tasks(self):
        all_users = self.project.get_users()
        all_tasks = self.project.get_tasks()
