from abc import ABC, abstractmethod

from projectsapp.entities.projects import Project
from projectsapp.entities.records import JournalRecord
from projectsapp.entities.task_category import TaskCategory
from projectsapp.entities.tasks import Task
from projectsapp.entities.users import User


class Visitor(ABC):
    @abstractmethod
    def visit_project(self, project: Project):
        pass

    @abstractmethod
    def visit_task(self, task: Task):
        pass

    @abstractmethod
    def visit_user(self, user: User):
        pass

    @abstractmethod
    def visit_journal_record(self, journal_record: JournalRecord):
        pass

    @abstractmethod
    def visit_task_category(self, task_category: TaskCategory):
        pass


class ChoicesVisitor(Visitor):
    def visit_user(self, user):
        return (user.id, user.username)

    def visit_project(self, project):
        return (project.id, project.name)

    def visit_task(self, task):
        return (task.id, task.name)

    def visit_task_category(self, task_category):
        return (task_category.id, task_category.name)

    def visit_journal_record(self, journal_record):
        return (journal_record.id, journal_record.date)
