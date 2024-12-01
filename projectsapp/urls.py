from django.urls import path
from . import views

app_name = "projectsapp"

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("create_project", views.create_project, name="create_project"),
    path("projects", views.projects, name="projects"),	
]
