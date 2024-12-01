from django.urls import path
from . import views

app_name = "projectsapp"

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("create_project", views.create_project, name="create_project"),
    path("projects", views.projects, name="projects"),
    path("projects/<uuid:project_id>/create_task/", views.create_task, name="create_task"),
  #Todo  path("projects/<str:project_id>/tasks/", views.tasks, name="tasks"),
  #Todo  path("projects/<str:project_id>/tasks/<str:task_id>/", views.task, name="task"),
    path("projects/<uuid:project_id>/", views.project, name="project"),
]
