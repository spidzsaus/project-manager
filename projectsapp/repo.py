from typing import Callable
from uuid import UUID
from datetime import datetime

from projectsapp.models import UserModel, TaskAssignmentModel, TaskModel, ProjectModel, MembershipModel

from projectsapp.entities.projects import Project
from projectsapp.entities.tasks import Task
from projectsapp.entities.users import User

class Repo:
    def get_user_by_id(self, id: UUID) -> User:
        res = UserModel.objects.filter(id=id).first()
        return res and res.as_entity(self)
    
    def get_project_by_id(self, id: UUID) -> Project:
        res = ProjectModel.objects.filter(id=id).first()
        return res and res.as_entity(self)
    
    def get_task_by_id(self, id: UUID) -> Task:
        res = TaskModel.objects.filter(id=id).first()
        return res and res.as_entity(self)
    
    def get_tasks_for_user(self, user: User, project: Project):
        res = TaskModel.objects.filter(taskassignment__user__id=user.id, project__id=project.id)
        return (model.as_entity(self) for model in res)
    
    def get_tasks_for_project(self, project: Project):
        res = TaskModel.objects.filter(project__id=project.id)
        return (model.as_entity(self) for model in res)

    def get_projects_for_user(self, user: User):
        res = ProjectModel.objects.filter(membership__user__id=user.id)
        return (model.as_entity(self) for model in res)
    
    def get_users_for_project(self, project: Project):
        return UserModel.objects.filter(membership__project__id=project.id)

    def get_users_for_task(self, task: TaskModel):
        res = UserModel.objects.filter(taskassignment__task=task)
        return (model.as_entity(self) for model in res)

    def add_user_to_project(self, user: User, project: Project):
        user_model = UserModel.objects.filter(id=user.id).first()
        project_model = ProjectModel.objects.filter(id=project.id).first()

        if not user_model or not project_model:
            return

        membership = MembershipModel(user=user_model, project=project_model, is_admin=False)
        membership.save()

    
    def remove_user_from_project(self, user: User, project: Project):
        memberships = MembershipModel.objects.filter(user__id=user.id, project__id=project.id)
        memberships.delete()

    def assign_task_to_user(self, user: User, task: Task):
        user_model = UserModel.objects.filter(id=user.id).first()
        task_model = TaskModel.objects.filter(id=task.id).first()

        if not user_model or not task_model:
            return

        task_assignment = TaskAssignmentModel(user=user_model, task=task_model)
        task_assignment.save()
        return task_assignment
    
    def unassign_user_from_task(self, user: User, task: Task):
        task_assignments = TaskAssignmentModel.objects.filter(user__id=user.id, task__id=task.id)
        task_assignments.delete()

    def update_project(self, project: Project):
        project_model = ProjectModel.objects.filter(id=project.id).first()
        if not project_model:
            return
        project_model.name = project.name
        # ...
        project_model.save()


    def update_task(self, task: Task):
        task_model = TaskModel.objects.filter(id=task.id).first()
        if not task_model:
            return
        task_model.name = task.name
        task_model.status = task.status
        task_model.end_date = task.end_date

        # ...
        task_model.save()

    def update_user(self, user: User):
        user_model = UserModel.objects.filter(id=user.id).first()
        if not user_model:
            return
        user_model.name = user.name
        # ...
        user_model.save()
