from django.urls import path

from . import views

app_name = "projectsapp"

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("create_project", views.create_project, name="create_project"),
    path("projects", views.projects, name="projects"),
    path(
        "projects/<uuid:project_id>/create_task/", views.create_task, name="create_task"
    ),
    # Todo  path("projects/<str:project_id>/tasks/", views.tasks, name="tasks"),
    # Todo  path("projects/<str:project_id>/tasks/<str:task_id>/", views.task, name="task"),
    path("projects/<uuid:project_id>/", views.project, name="project"),
    # path(
    #    "change_task_status/<uuid:project_id>/<uuid:task_id>/",
    #    views.change_task_status,
    #    name="change_task_status",
    # ),
    path(
        "start_task/<uuid:project_id>/<uuid:task_id>/",
        views.start_task,
        name="start_task",
    ),
    path(
        "finish_task/<uuid:project_id>/<uuid:task_id>/",
        views.finish_task,
        name="finish_task",
    ),
    path(
        "delete_task/<uuid:project_id>/<uuid:task_id>/",
        views.delete_task,
        name="delete_task",
    ),
    path(
        "manage_project/<uuid:project_id>/", views.manage_project, name="manage_project"
    ),
    path("invite_user/<uuid:project_id>/", views.invite_user, name="invite_user"),
    path(
        "delete_project/<uuid:project_id>/", views.delete_project, name="delete_project"
    ),
    path(
        "manage_task/<uuid:project_id>/<uuid:task_id>/",
        views.manage_task,
        name="manage_task",
    ),
    path(
        "projects/<uuid:project_id>/tasks/<uuid:task_id>/update/",
        views.update_task,
        name="update_task",
    ),
    path(
        "projects/<uuid:project_id>/tasks/<uuid:task_id>/assign-user/",
        views.assign_user_to_task,
        name="assign_user",
    ),
    path(
        "projects/<uuid:project_id>/tasks/<uuid:task_id>/remove-user/<uuid:user_id>/",
        views.remove_user_from_task,
        name="remove_user",
    ),
    path(
        "projects/<uuid:project_id>/tasks/<uuid:task_id>/assign-dependency/",
        views.assign_dependency_to_task,
        name="assign_dependency",
    ),
    path(
        "projects/<uuid:project_id>/tasks/<uuid:task_id>/remove-dependency/<uuid:dep_id>/",
        views.remove_dependency_from_task,
        name="remove_dependency",
    ),
    path(
        "projects/<uuid:project_id>/categories/<uuid:category_id>/update/",
        views.update_task_category,
        name="update_task_category",
    ),
    path(
        "projects/<uuid:project_id>/categories/<uuid:category_id>/add-user/",
        views.add_user_to_category,
        name="add_user_to_category",
    ),
    path(
        "projects/<uuid:project_id>/categories/<uuid:category_id>/remove-user/<uuid:user_id>/",
        views.remove_user_from_category,
        name="remove_user_from_category",
    ),
    path(
        "projects/<uuid:project_id>/categories/<uuid:category_id>/add-task/",
        views.add_task_to_category,
        name="add_task_to_category",
    ),
    path(
        "projects/<uuid:project_id>/categories/<uuid:category_id>/remove-task/<uuid:task_id>/",
        views.remove_task_from_category,
        name="remove_task_from_category",
    ),
    path(
        "projects/<uuid:project_id>/create-category/",
        views.create_task_category,
        name="create_task_category",
    ),
    path(
        "projects/<uuid:project_id>/categories/<uuid:category_id>/",
        views.manage_task_category,
        name="manage_task_category",
    ),
    path(
        "projects/<uuid:project_id>/categories/<uuid:category_id>/delete/",
        views.delete_task_category,
        name="delete_task_category",
    ),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("home/", views.index, name="home"),
    path(
        "projects/<uuid:project_id>/auto_assign/",
        views.auto_assign_tasks,
        name="autoassign",
    ),
]
