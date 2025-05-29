from datetime import datetime
from typing import Callable, Iterable
from uuid import UUID

from projectsapp.entities.projects import Project
from projectsapp.entities.records import JournalRecord
from projectsapp.entities.tasks import Task
from projectsapp.entities.users import User
from projectsapp.entities.task_category import TaskCategory
from projectsapp.models import (
    JournalRecordModel,
    MembershipModel,
    ProjectModel,
    TaskAssignmentModel,
    TaskDependencyModel,
    TaskModel,
    UserModel,
    TaskCategoryModel,
    TaskCategoryAssignmentModel,
    UserTaskCategoryAssignmentModel,
)

# Docstrings and code comments are in Russian.
# Докстринги и комментарии на русском


class Repo:
    def insert_user(self, user: User) -> User | None:
        """
        Добавляет пользователя в репозиторий.

        Если пользователь уже существует, то метод ничего не делает.

        :param user: пользователь, который будет добавлен
        :return: добавленный пользователь
        """

        user_model = UserModel(id=user.id, name=user.name)  # ...
        user_model.save()
        return user_model.as_entity(self)

    def insert_project(self, project: Project) -> Project | None:
        """
        Добавляет проект в репозиторий.

        Если проект уже существует, то метод ничего не делает.

        :param project: проект, который будет добавлен
        :return: добавленный проект
        """

        project_model = ProjectModel(id=project.id, name=project.name)  # ...
        project_model.save()
        return project_model.as_entity(self)

    def insert_task(self, task: Task) -> Task:
        """
        Добавляет задачу в репозиторий.

        Если задача уже существует, то метод ничего не делает.

        :param task: задача, которая будет добавлена
        :return: добавленная задача
        """

        task_model = TaskModel(
            id=task.id,
            name=task.name,
            description=task.description,
            status=task.status.value,
            end_date=task.end_date,
            parent_project=ProjectModel.objects.get(id=task.parent_project.id),
            # ...
        )
        task_model.save()
        return task_model.as_entity(self)

    def insert_journal_record(self, record: JournalRecord) -> JournalRecord:
        """
        Добавляет запись в журнал в репозиторий.

        :param record: запись в журнал, которая будет добавлена
        :return: добавленная запись в журнал
        """

        record_model = JournalRecordModel(
            id=record.id,
            user=record.user and UserModel.objects.get(id=record.user.id),
            task=record.task and TaskModel.objects.get(id=record.task.id),
            project=record.project and ProjectModel.objects.get(id=record.project.id),
            date=record.date,
            event_type=record.event_type.value,
        )
        record_model.save()
        return record_model.as_entity(self)

    def get_user_by_id(self, id: UUID) -> User | None:
        """
        Возвращает пользователя по его id или None, если такого пользователя нет.

        :param id: id пользователя
        :return: пользователь или None
        """

        res = UserModel.objects.filter(id=id).first()
        return res and res.as_entity(self)

    def get_user_by_name(self, name: str) -> User | None:
        """
        Возвращает пользователя по его имени или None, если такого пользователя нет.

        :param name: имя пользователя
        :return: пользователь или None
        """

        res = UserModel.objects.filter(name=name).first()
        return res and res.as_entity(self)

    def get_project_by_id(self, id: UUID) -> Project | None:
        """
        Возвращает проект по его id или None, если такого проекта нет.

        :param id: id проекта
        :return: проект или None
        """

        res = ProjectModel.objects.filter(id=id).first()
        return res and res.as_entity(self)

    def get_task_by_id(self, id: UUID) -> Task | None:
        """
        Возвращает задачу по ее id или None, если такой задачи нет.

        :param id: id задачи
        :return: задача или None
        """

        res = TaskModel.objects.filter(id=id).first()
        return res and res.as_entity(self)

    def get_tasks_for_user(
        self, user: User, project: Project | None = None, sort_by_status: bool = False
    ):
        """
        Возвращает задачи, которые назначены пользователю в рамках конкретного проекта.

        :param user: пользователь
        :param project: проект
        :param sort_by_status: сортировать ли задачи по статусу (опционально)
        :return: задачи
        """

        res = (
            TaskModel.objects.filter(taskassignmentmodel__user__id=user.id)
            if project is None
            else TaskModel.objects.filter(
                taskassignmentmodel__user__id=user.id, parent_project__id=project.id
            )
        )
        if sort_by_status:
            res = res.order_by("status")
        return (model.as_entity(self) for model in res)

    def get_tasks_for_user_grouped_by_status(
        self, user: User, project: Project | None = None
    ) -> dict[Task.Status, Iterable[Task]]:

        def model_status_to_entity_status(status):
            match status:
                case TaskModel.Status.TODO:
                    return Task.Status.TODO
                case TaskModel.Status.IN_PROCESS:
                    return Task.Status.IN_PROCESS
                case TaskModel.Status.DONE:
                    return Task.Status.DONE

        tasks_by_statuses = {}
        for status, display in TaskModel.Status.choices:
            res = (
                TaskModel.objects.filter(
                    taskassignmentmodel__user__id=user.id, status=status
                )
                if project is None
                else TaskModel.objects.filter(
                    taskassignmentmodel__user__id=user.id,
                    parent_project__id=project.id,
                    status=status,
                )
            )
            tasks_by_statuses[model_status_to_entity_status(status)] = (
                model.as_entity(self) for model in res
            )
        return tasks_by_statuses

    def get_tasks_for_project(self, project: Project):
        """
        Возвращает задачи, которые принадлежат конкретному проекту.

        :param project: проект
        :return: задачи
        """

        res = TaskModel.objects.filter(parent_project__id=project.id)
        return (model.as_entity(self) for model in res)

    def get_projects_for_user(self, user: User):
        """
        Возвращает проекты, в командах которых состоит пользователь.

        :param user: пользователь
        :return: проекты
        """

        res = ProjectModel.objects.filter(membershipmodel__user__id=user.id)
        return (model.as_entity(self) for model in res)

    def get_users_for_project(self, project: Project):
        """
        Возвращает пользователей, которые состоят в команде данного проекта.

        :param project: проект
        :return: пользователи
        """

        res = UserModel.objects.filter(
            membershipmodel__project__id=project.id
        ).order_by("membershipmodel__is_admin")
        return (model.as_entity(self) for model in res)

    def get_users_for_task(self, task: Task):
        """
        Возвращает пользователей, которые назначены на задачу.

        :param task: задача
        :return: пользователи
        """

        res = UserModel.objects.filter(taskassignmentmodel__task__id=task.id)
        return (model.as_entity(self) for model in res)

    def get_journal_records_for_task(self, task: Task):
        """
        Возвращает записи журнала для задачи.

        :param task: задача
        :return: записи журнала
        """

        res = JournalRecordModel.objects.filter(task__id=task.id)
        return (model.as_entity(self) for model in res)

    def get_journal_records_for_user(self, user: User):
        """
        Возвращает записи журнала для пользователя.

        :param user: пользователь
        :return: записи журнала
        """

        res = JournalRecordModel.objects.filter(user__id=user.id)
        return (model.as_entity(self) for model in res)

    def get_journal_records_for_project(self, project: Project):
        """
        Возвращает записи журнала для проекта.

        :param project: проект
        :return: записи журнала
        """

        res = JournalRecordModel.objects.filter(task__parent_project__id=project.id)
        return (model.as_entity(self) for model in res)

    def get_journal_record_by_id(self, id: UUID) -> JournalRecord | None:
        """
        Возвращает запись журнала по ее id или None, если такой записи нет.

        :param id: id записи журнала
        :return: запись журнала или None
        """

        res = JournalRecordModel.objects.filter(id=id).first()
        return res and res.as_entity(self)

    def add_user_to_project(self, user: User, project: Project):
        """
        Добавляет пользователя в проект.

        :param user: пользователь, который будет добавлен
        :param project: проект, в котором будет добавлен пользователь
        """

        user_model = UserModel.objects.filter(id=user.id).first()
        project_model = ProjectModel.objects.filter(id=project.id).first()

        if not user_model or not project_model:
            return

        membership = MembershipModel(
            user=user_model, project=project_model, is_admin=False
        )
        membership.save()

    def add_owner_to_project(self, user: User, project: Project):
        """
        Добавляет владельца проекта в проект.
        То же самое, что и add_user_to_project, но пользователь сразу
        получает права администратора.

        :param user: владелец проекта
        :param project: проект, в котором будет добавлен владелец
        """

        user_model = UserModel.objects.filter(id=user.id).first()
        project_model = ProjectModel.objects.filter(id=project.id).first()

        if not user_model or not project_model:
            return

        membership = MembershipModel(
            user=user_model, project=project_model, is_admin=True
        )
        membership.save()

    def promote_user_in_project(self, user: User, project: Project):
        """
        Повышает права пользователя в проекте.

        :param user: пользователь, которого нужно повысить
        :param project: проект, в котором нужно повысить пользователя
        """

        membership = MembershipModel.objects.filter(
            user__id=user.id, project__id=project.id
        ).first()
        if membership is None:
            return
        membership.is_admin = True
        membership.save()

    def remove_user_from_project(self, user: User, project: Project):
        """
        Удаляет пользователя из проекта.

        :param user: пользователь, которого нужно удалить
        :param project: проект, из которого нужно удалить пользователя
        """

        memberships = MembershipModel.objects.filter(
            user__id=user.id, project__id=project.id
        )
        memberships.delete()

    def assign_task_to_user(self, user: User, task: Task):
        """
        Назначает задачу пользователю.

        :param user: пользователь
        :param task: задача
        """

        user_model = UserModel.objects.filter(id=user.id).first()
        task_model = TaskModel.objects.filter(id=task.id).first()

        if not user_model or not task_model:
            return

        task_assignment = TaskAssignmentModel(user=user_model, task=task_model)
        task_assignment.save()
        return task_assignment

    def unassign_user_from_task(self, user: User, task: Task):
        """
        Удаляет назначение задачи пользователю.

        :param user: пользователь
        :param task: задача
        """

        task_assignments = TaskAssignmentModel.objects.filter(
            user__id=user.id, task__id=task.id
        )
        task_assignments.delete()

    def update_project(self, project: Project):
        """
        Обновляет данные проекта.

        :param project: проект, который будет обновлен
        """

        project_model = ProjectModel.objects.filter(id=project.id).first()
        if not project_model:
            return
        project_model.name = project.name
        # ...
        project_model.save()

    def update_task(self, task: Task):
        """
        Обновляет данные задачи.

        :param task: задача, которая будет обновлена
        """

        task_model = TaskModel.objects.filter(id=task.id).first()
        if not task_model:
            return
        task_model.name = task.name
        task_model.status = task.status.value
        task_model.end_date = task.end_date
        task_model.description = task.description

        # ...
        task_model.save()

    def update_user(self, user: User):
        """
        Обновляет данные пользователя.

        :param user: пользователь, который будет обновлен
        """

        user_model = UserModel.objects.filter(id=user.id).first()
        if not user_model:
            return
        user_model.name = user.name
        # ...
        user_model.save()

    def is_user_admin_in_project(self, user: User, project: Project) -> bool:
        membership = MembershipModel.objects.filter(
            user__id=user.id, project__id=project.id
        ).first()
        return not not (membership and membership.is_admin)

    def delete_project(self, project: Project):
        project_model = ProjectModel.objects.filter(id=project.id).first()
        if not project_model:
            return
        project_model.delete()

    def delete_task(self, task: Task):
        task_model = TaskModel.objects.filter(id=task.id).first()
        if not task_model:
            return
        task_model.delete()

    def delete_user(self, user: User):
        user_model = UserModel.objects.filter(id=user.id).first()
        if not user_model:
            return
        user_model.delete()

    def get_tasks_dependent_on_task(self, task: Task) -> Iterable[Task]:
        """
        Возвращает задачи, которые зависят от данной задачи.

        :param task: задача
        :return: задачи, зависящие от данной
        """
        task_dependency_models = TaskDependencyModel.objects.filter(
            depends_on__id=task.id
        )
        return (
            task_dependency_model.task.as_entity(self)
            for task_dependency_model in task_dependency_models
        )

    def get_dependency_tasks_for_task(self, task: Task) -> Iterable[Task]:
        """
        Возвращает задачи, от которых зависит данная задача.

        :param task: задача
        :return: задачи, от которых зависит данная
        """
        task_dependency_models = TaskDependencyModel.objects.filter(task__id=task.id)
        return (
            task_dependency_model.depends_on.as_entity(self)
            for task_dependency_model in task_dependency_models
        )

    def add_task_dependency(self, task: Task, depends_on: Task):
        """
        Добавляет зависимость между задачами.

        :param task: задача, которая будет зависеть
        :param depends_on: задача, от которой будет зависеть
        """
        task_model = TaskModel.objects.filter(id=task.id).first()
        depends_on_model = TaskModel.objects.filter(id=depends_on.id).first()

        if not task_model or not depends_on_model:
            return

        task_dependency_model = TaskDependencyModel(
            task=task_model, depends_on=depends_on_model
        )
        task_dependency_model.save()

    def remove_task_dependency(self, task: Task, dependency: Task):
        """
        Удаляет зависимость задачи.

        :param task: задача
        :param dependency: зависимость
        """

        task_dependency_model = TaskDependencyModel.objects.filter(
            task__id=task.id, depends_on__id=dependency.id
        )

        task_dependency_model.delete()

    def get_tasks_in_task_category(self, task_category: TaskCategory) -> Iterable[Task]:
        res = TaskModel.objects.filter(
            taskcategoryassignmentmodel__task_category__id=task_category.id
        )
        return (model.as_entity(self) for model in res)

    def get_users_for_task_category(
        self, task_category: TaskCategory
    ) -> Iterable[User]:
        res = UserModel.objects.filter(
            usertaskcategoryassignmentmodel__task_category__id=task_category.id
        )
        return (model.as_entity(self) for model in res)

    def add_task_to_task_category(self, task: Task, task_category: TaskCategory):
        task_model = TaskModel.objects.filter(id=task.id).first()
        task_category_model = TaskCategoryModel.objects.filter(
            id=task_category.id
        ).first()

        if not task_model or not task_category_model:
            return

        task_category_assignment_model = TaskCategoryAssignmentModel(
            task=task_model, task_category=task_category_model
        )
        task_category_assignment_model.save()

    def add_user_to_task_category(self, user: User, task_category: TaskCategory):
        user_model = UserModel.objects.filter(id=user.id).first()
        task_category_model = TaskCategoryModel.objects.filter(
            id=task_category.id
        ).first()

        if not user_model or not task_category_model:
            return

        user_task_category_assignment_model = UserTaskCategoryAssignmentModel(
            user=user_model, task_category=task_category_model
        )
        user_task_category_assignment_model.save()

    def insert_task_category(self, task_category: TaskCategory):
        task_category_model = TaskCategoryModel(
            id=task_category.id,
            name=task_category.name,
            project=ProjectModel.objects.get(id=task_category.project.id),
        )
        task_category_model.save()

    def get_task_categories_for_project(
        self, project: Project
    ) -> Iterable[TaskCategory]:
        res = TaskCategoryModel.objects.filter(project__id=project.id)
        return (model.as_entity(self) for model in res)

    def get_task_categories_for_task(self, task: Task) -> Iterable[TaskCategory]:
        res = TaskCategoryAssignmentModel.objects.filter(task__id=task.id)
        return (model.task_category.as_entity(self) for model in res)

    def get_task_categories_for_user(self, user: User) -> Iterable[TaskCategory]:
        res = UserTaskCategoryAssignmentModel.objects.filter(user__id=user.id)
        return (model.task_category.as_entity(self) for model in res)

    def get_task_category_by_id(self, task_category_id: UUID) -> TaskCategory | None:
        res = TaskCategoryModel.objects.filter(id=task_category_id).first()

        return res and res.as_entity(self)

    def update_task_category(self, task_category: TaskCategory):
        task_category_model = TaskCategoryModel.objects.filter(
            id=task_category.id
        ).first()

        if not task_category_model:
            return

        task_category_model.name = task_category.name
        task_category_model.description = task_category.description
        task_category_model.save()

        return task_category

    def delete_task_category(self, task_category: TaskCategory):
        task_category_model = TaskCategoryModel.objects.filter(
            id=task_category.id
        ).first()

        if not task_category_model:
            return

        task_category_model.delete()

    def remove_task_from_task_category(self, task: Task, task_category: TaskCategory):
        task_model = TaskModel.objects.filter(id=task.id).first()
        task_category_model = TaskCategoryModel.objects.filter(
            id=task_category.id
        ).first()

        if not task_model or not task_category_model:
            return

        task_category_assignment_model = TaskCategoryAssignmentModel.objects.filter(
            task=task_model, task_category=task_category_model
        )

        task_category_assignment_model.delete()

    def remove_user_from_task_category(self, user: User, task_category: TaskCategory):
        user_model = UserModel.objects.filter(id=user.id).first()
        task_category_model = TaskCategoryModel.objects.filter(
            id=task_category.id
        ).first()

        if not user_model or not task_category_model:
            return

        user_task_category_assignment_model = (
            UserTaskCategoryAssignmentModel.objects.filter(
                user=user_model, task_category=task_category_model
            )
        )

        user_task_category_assignment_model.delete()
