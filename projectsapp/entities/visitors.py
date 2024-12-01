from abc import ABC, abstractmethod

from projectsapp.entities.projects import Project
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

class ChoicesVisitor(Visitor):
    def visit_user(self, user):
        return (user.id, user.name)
    
    def visit_project(self, project):
        return (project.id, project.name)
    
    def visit_task(self, task):
        return (task.id, task.name)