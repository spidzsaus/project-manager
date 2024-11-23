from django.urls import path
from . import views

app_name = 'projectsapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    #path('projects/<int:project_id>', views.project, name='project'),
    #path('projects/<int:project_id>/members', views.members, name='members'),
    #path('projects/<int:project_id>/tasks', views.tasks, name='tasks'), 
]