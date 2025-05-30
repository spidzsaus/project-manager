from uuid import UUID
import datetime

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate as old_authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect


from projectsapp.analysis_unit import AnalysisUnit
from projectsapp.auto_task_assigner import AutoTaskAssigner
from projectsapp.entities.projects import Project
from projectsapp.entities.tasks import Task, CyclicDependencyError, SelfDependencyError
from projectsapp.entities.users import User
from projectsapp.entities.task_category import TaskCategory
from projectsapp.entities.visitors import ChoicesVisitor
from projectsapp.forms import (
    CreateProjectForm,
    CreateTaskForm,
    InviteUserForm,
    AssignUserForm,
    AssignDependencyForm,
    AddTaskToCategoryForm,
    AddUserToCategoryForm,
    LoginForm,
    SignupForm,
)
from projectsapp.models import UserModel
from projectsapp.repo import Repo


def authenticate(request, repo=None) -> User:
    if repo is None:
        repo = Repo()
    user: UserModel = request.user
    assert user is not None
    return user.as_entity(repo)


def home(request):
    return render(request, "home.html")


@login_required
def create_project(request):
    repo = Repo()
    user = authenticate(request, repo)
    assert user is not None

    if request.method == "POST":
        form = CreateProjectForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]

            project = Project(name=name, repo=Repo())
            repo.insert_project(project)

            project.add_owner(user)

            return redirect("projectsapp:projects")
    else:
        form = CreateProjectForm()

    return render(request, "create_project.html", {"form": form})


@login_required
def create_task(request, project_id: UUID):
    repo = Repo()
    user = authenticate(request, repo)

    project = repo.get_project_by_id(project_id)

    assert project is not None  # todo: handle this case

    users_choices = map(
        lambda u: u.accept_visitor(ChoicesVisitor()), project.get_users()
    )
    tasks_choices = map(
        lambda t: t.accept_visitor(ChoicesVisitor()), project.get_tasks()
    )

    if request.method == "POST":
        form = CreateTaskForm(users_choices, tasks_choices, request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            end_date = form.cleaned_data["end_date"]
            dependencies = form.cleaned_data["depends_on"]
            assigned_to = form.cleaned_data["users"]

            task = Task(
                name=name,
                description=description,
                end_date=end_date,
                parent_project=project,
                repo=repo,
            )
            repo.insert_task(task)

            for dependency_id in dependencies:
                dependency_task = repo.get_task_by_id(UUID(dependency_id))
                assert dependency_task is not None  # todo: handle this case
                task.add_dependency(dependency_task)

            assigned_to_user = repo.get_user_by_id(UUID(assigned_to))
            assert assigned_to_user is not None  # todo: handle this case

            task.assign_user(assigned_to_user)

        else:
            raise Exception("Invalid form", form.errors, form.non_field_errors)

    else:
        form = CreateTaskForm(
            users=users_choices, tasks=project.get_tasks()
        )  # todo: pagination

    return redirect(
        f"{reverse('projectsapp:manage_project', args=[project_id])}?no_fade=True"
    )


@login_required
def invite_user(request, project_id: UUID):
    repo = Repo()
    user = authenticate(request, repo)

    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case

    if request.method == "POST":
        form = InviteUserForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]

            repo = Repo()
            user = repo.get_user_by_username(username)
            if not user:
                return HttpResponseNotFound("User not found")

            project.add_user(user)

    return redirect(
        f"{reverse('projectsapp:manage_project', args=[project_id])}?no_fade=True"
    )


def create_task_form(project_id: UUID) -> CreateTaskForm:
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case

    users_choices = map(
        lambda u: u.accept_visitor(ChoicesVisitor()), project.get_users()
    )

    tasks_choices = map(
        lambda t: t.accept_visitor(ChoicesVisitor()), project.get_tasks()
    )

    return CreateTaskForm(users_choices, tasks_choices)  # todo: pagination


def assign_user_form(project_id: UUID) -> AssignUserForm:
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case

    user_choices = map(
        lambda u: u.accept_visitor(ChoicesVisitor()), project.get_users()
    )

    return AssignUserForm(user_choices)


def assign_dependency_form(project_id: UUID) -> AssignDependencyForm:
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case

    tasks_choices = map(
        lambda t: t.accept_visitor(ChoicesVisitor()), project.get_tasks()
    )
    return AssignDependencyForm(tasks_choices)


def invite_user_form(project_id: UUID) -> InviteUserForm:
    repo = Repo()
    project = repo.get_project_by_id(project_id)

    return InviteUserForm()


@login_required
def project(request, project_id: UUID):
    repo = Repo()
    no_fade = request.GET.get("no_fade") == "True"
    user = authenticate(request, repo)
    assert user is not None

    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case
    is_admin = user.is_admin_in_project(project)

    tasks_by_statuses = repo.get_tasks_for_user_grouped_by_status(user, project)

    complete_tasks = list(tasks_by_statuses.get(Task.Status.DONE, []))
    active_tasks = list(tasks_by_statuses.get(Task.Status.IN_PROCESS, []))
    todo_tasks = list(tasks_by_statuses.get(Task.Status.TODO, []))

    has_tasks = not not (complete_tasks or active_tasks or todo_tasks)

    print(has_tasks, complete_tasks, active_tasks, todo_tasks)
    return render(
        request,
        "project.html",
        {
            "project": project,
            "complete_tasks": list(complete_tasks),
            "active_tasks": list(active_tasks),
            "todo_tasks": list(todo_tasks),
            "has_tasks": has_tasks,
            "no_fade": no_fade,
            "is_admin": is_admin,
            "task_dependencies": AnalysisUnit(project)._dependencies_data(),
        },
    )


@login_required
def manage_project(request, project_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case

    no_fade = request.GET.get("no_fade") == "True"

    if not user.is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    analysis = AnalysisUnit(project).cook_data()

    params = {
        "project": project,
        "create_task_form": create_task_form(project_id),
        "no_fade": no_fade,
        "invite_user_form": invite_user_form(project_id),
        "records": project.get_journal_records(),
        "task_categories": project.get_task_categories(),
    }

    params.update(analysis)

    return render(request, "manage_project.html", params)


@login_required
def manage_task(request, project_id: UUID, task_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case
    task = repo.get_task_by_id(task_id)
    assert task is not None  # todo: handle this case

    no_fade = request.GET.get("no_fade", "False") == "True"
    is_admin = user.is_admin_in_project(project)

    return render(
        request,
        "manage_task.html",
        {
            "project": project,
            "task": task,
            "assign_user_form": assign_user_form(project_id),
            "assign_dependency_form": assign_dependency_form(project_id),
        },
    )


@login_required
def update_task(request, project_id: UUID, task_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task = repo.get_task_by_id(task_id)

    if not project or not task:
        return HttpResponseNotFound("Project or Task not found")

    if not user.is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        end_date = request.POST.get("end_date")

        task.update_details(name=name, description=description, end_date=end_date)

    return redirect(
        f"{reverse('projectsapp:manage_task', args=[project_id, task_id])}?no_fade=True"
    )


@login_required
def assign_user_to_task(request, project_id: UUID, task_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task = repo.get_task_by_id(task_id)

    if not project or not task:
        return HttpResponseNotFound("Project or Task not found")

    if not user.is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    if request.method == "POST":
        form = AssignUserForm(
            map(lambda u: u.accept_visitor(ChoicesVisitor()), project.get_users()),
            request.POST,
        )

        if form.is_valid():
            user_id = form.cleaned_data["user"]
            user_to_assign = repo.get_user_by_id(UUID(user_id))
            if user_to_assign:
                task.assign_user(user_to_assign)

    return redirect(
        f"{reverse('projectsapp:manage_task', args=[project_id, task_id])}?no_fade=True"
    )


@login_required
def remove_user_from_task(request, project_id: UUID, task_id: UUID, user_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task = repo.get_task_by_id(task_id)
    user_to_remove = repo.get_user_by_id(user_id)

    if not project or not task or not user_to_remove:
        return HttpResponseNotFound("Project, Task or User not found")

    if not user.is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    task.unassign_user(user_to_remove)

    return redirect(
        f"{reverse('projectsapp:manage_task', args=[project_id, task_id])}?no_fade=True"
    )


@login_required
def assign_dependency_to_task(request, project_id: UUID, task_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task = repo.get_task_by_id(task_id)

    if not project or not task:
        return HttpResponseNotFound("Project or Task not found")

    if not user.is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    if request.method == "POST":
        form = AssignDependencyForm(
            map(lambda t: t.accept_visitor(ChoicesVisitor()), project.get_tasks()),
            request.POST,
        )

        if form.is_valid():
            dependency_id = form.cleaned_data["dependency_task"]
            dependency = repo.get_task_by_id(UUID(dependency_id))
            if dependency:
                try:
                    task.add_dependency(dependency)
                except CyclicDependencyError:
                    messages.error(
                        request,
                        "Can't add cyclic dependency to task",
                        extra_tags="cyclic-dependency",
                    )
                except SelfDependencyError:
                    messages.error(
                        request,
                        "Task can't be dependent on itself",
                        extra_tags="self-dependency",
                    )

    return redirect(
        f"{reverse('projectsapp:manage_task', args=[project_id, task_id])}?no_fade=True"
    )


@login_required
def remove_dependency_from_task(request, project_id: UUID, task_id: UUID, dep_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task = repo.get_task_by_id(task_id)
    dependency = repo.get_task_by_id(dep_id)

    if not project or not task or not dependency:
        return HttpResponseNotFound("Project, Task or Dependency not found")

    if not user.is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    task.remove_dependency(dependency)

    return redirect(
        f"{reverse('projectsapp:manage_task', args=[project_id, task_id])}?no_fade=True"
    )


@login_required
def projects(request):
    """
    Тестовая страница, которая выводит карточки со всеми проектами, частью которых является
    пользователь.
    """

    user = authenticate(request)

    # Получение всех проектов, в которых участвует тестовый пользователь
    projects_list = user.get_projects()

    # Возвращаем страницу с карточками проектов.
    # Страница генерируется на основе шаблона test.html
    # с подстановкой списка проектов в параметр projects_list
    return render(request, "projects.html", {"projects_list": projects_list})


def index(request):
    return render(request, "index.html")


@login_required
def start_task(request, project_id: UUID, task_id: UUID):
    repo = Repo()
    task = repo.get_task_by_id(task_id)
    assert task is not None  # todo: handle this case
    if task.status == Task.Status.TODO:
        task.change_status(Task.Status.IN_PROCESS)
    return redirect(f"{reverse('projectsapp:project', args=[project_id])}?no_fade=True")


@login_required
def finish_task(request, project_id: UUID, task_id: UUID):
    repo = Repo()
    task = repo.get_task_by_id(task_id)
    assert task is not None  # todo: handle this case
    if task.status == Task.Status.IN_PROCESS:
        task.change_status(Task.Status.DONE)
    return redirect(f"{reverse('projectsapp:project', args=[project_id])}?no_fade=True")


@login_required
def change_task_status(request, project_id: UUID, task_id: UUID):
    repo = Repo()
    task = repo.get_task_by_id(task_id)
    assert task is not None  # todo: handle this case

    if request.method == "POST":
        status = Task.Status(int(request.POST["status"]))
        task.change_status(status)

    return redirect(f"{reverse('projectsapp:project', args=[project_id])}?no_fade=True")


@login_required
def delete_task(request, project_id: UUID, task_id: UUID):
    repo = Repo()
    task = repo.get_task_by_id(task_id)
    assert task is not None  # todo: handle this case

    user = authenticate(request)

    if not user.is_admin_in_project(task.parent_project):
        return HttpResponseForbidden("You are not admin in this project")

    if request.method == "POST":
        repo.delete_task(task)

    return redirect(
        f"{reverse('projectsapp:manage_project', args=[project_id])}?no_fade=True"
    )


@login_required
def delete_project(request, project_id: UUID):
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case

    user = authenticate(request)

    if not user.is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    if request.method == "POST":
        repo.delete_project(project)

    return redirect("projectsapp:projects")


@login_required
def update_task_category(request, project_id: UUID, category_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task_category = repo.get_task_category_by_id(category_id)

    if not project or not task_category:
        messages.error(request, "Project or Task Category not found")
        return redirect(reverse("projectsapp:projects"))

    if not user.is_admin_in_project(project):
        messages.error(request, "You are not authorized to perform this action")
        return redirect(reverse("projectsapp:projects"))

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        task_category.update_details(name=name, description=description)
        messages.success(request, "Category details updated successfully")

    return redirect(
        f"{reverse('projectsapp:manage_task_category', args=[project_id, category_id])}?no_fade=True"
    )


@login_required
def add_user_to_category(request, project_id: UUID, category_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task_category = repo.get_task_category_by_id(category_id)

    if not project or not task_category:
        messages.error(request, "Project or Task Category not found")
        return redirect(reverse("projectsapp:projects"))

    if not user.is_admin_in_project(project):
        messages.error(request, "You are not authorized to perform this action")
        return redirect(reverse("projectsapp:projects"))

    if request.method == "POST":
        form = AddUserToCategoryForm(
            map(lambda u: u.accept_visitor(ChoicesVisitor()), project.get_users()),
            request.POST,
        )

        if form.is_valid():
            user_id = form.cleaned_data["user"]
            user_to_add = repo.get_user_by_id(UUID(user_id))
            if user_to_add:
                try:
                    task_category.add_user(user_to_add)
                    messages.success(request, f"{user_to_add.name} added to category")
                except Exception as e:
                    messages.error(request, f"Error adding user: {str(e)}")
            else:
                messages.error(request, "User not found")
        else:
            messages.error(request, "Invalid form submission")

    return redirect(
        f"{reverse('projectsapp:manage_task_category', args=[project_id, category_id])}?no_fade=True"
    )


@login_required
def remove_user_from_category(
    request, project_id: UUID, category_id: UUID, user_id: UUID
):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task_category = repo.get_task_category_by_id(category_id)
    user_to_remove = repo.get_user_by_id(user_id)

    if not project or not task_category or not user_to_remove:
        messages.error(request, "Project, Category or User not found")
        return redirect(reverse("projectsapp:projects"))

    if not user.is_admin_in_project(project):
        messages.error(request, "You are not authorized to perform this action")
        return redirect(reverse("projectsapp:projects"))

    try:
        task_category.remove_user(user_to_remove)
        messages.success(request, f"{user_to_remove.name} removed from category")
    except Exception as e:
        messages.error(request, f"Error removing user: {str(e)}")

    return redirect(
        f"{reverse('projectsapp:manage_task_category', args=[project_id, category_id])}?no_fade=True"
    )


@login_required
def add_task_to_category(request, project_id: UUID, category_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task_category = repo.get_task_category_by_id(category_id)

    if not project or not task_category:
        messages.error(request, "Project or Task Category not found")
        return redirect(reverse("projectsapp:projects"))

    if not user.is_admin_in_project(project):
        messages.error(request, "You are not authorized to perform this action")
        return redirect(reverse("projectsapp:projects"))

    if request.method == "POST":
        form = AddTaskToCategoryForm(
            map(lambda t: t.accept_visitor(ChoicesVisitor()), project.get_tasks()),
            request.POST,
        )

        if form.is_valid():
            task_id = form.cleaned_data["task"]
            task_to_add = repo.get_task_by_id(UUID(task_id))
            if task_to_add:
                try:
                    task_category.add_task(task_to_add)
                    messages.success(
                        request, f"Task '{task_to_add.name}' added to category"
                    )
                except Exception as e:
                    messages.error(request, f"Error adding task: {str(e)}")
            else:
                messages.error(request, "Task not found")
        else:
            messages.error(request, "Invalid form submission")

    return redirect(
        f"{reverse('projectsapp:manage_task_category', args=[project_id, category_id])}?no_fade=True"
    )


@login_required
def remove_task_from_category(
    request, project_id: UUID, category_id: UUID, task_id: UUID
):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task_category = repo.get_task_category_by_id(category_id)
    task_to_remove = repo.get_task_by_id(task_id)

    if not project or not task_category or not task_to_remove:
        messages.error(request, "Project, Category or Task not found")
        return redirect(reverse("projectsapp:projects"))

    if not user.is_admin_in_project(project):
        messages.error(request, "You are not authorized to perform this action")
        return redirect(reverse("projectsapp:projects"))

    try:
        task_category.remove_task(task_to_remove)
        messages.success(request, f"Task '{task_to_remove.name}' removed from category")
    except Exception as e:
        messages.error(request, f"Error removing task: {str(e)}")

    return redirect(
        f"{reverse('projectsapp:manage_task_category', args=[project_id, category_id])}?no_fade=True"
    )


def add_user_to_category_form(task_category: TaskCategory) -> AddUserToCategoryForm:

    project = task_category.project
    category_users = task_category.get_users()

    users_choices = map(
        lambda u: u.accept_visitor(ChoicesVisitor()),
        filter(lambda u: u not in category_users, project.get_users()),
    )

    return AddUserToCategoryForm(users_choices)


def add_task_to_category_form(task_category: TaskCategory) -> AddTaskToCategoryForm:

    project = task_category.project
    category_tasks = task_category.get_tasks()

    tasks_choices = map(
        lambda t: t.accept_visitor(ChoicesVisitor()),
        filter(
            lambda t: t not in category_tasks,
            project.get_tasks(),
        ),
    )

    return AddTaskToCategoryForm(tasks_choices)


@login_required
def manage_task_category(request, project_id: UUID, category_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task_category = repo.get_task_category_by_id(category_id)

    if not project or not task_category:
        messages.error(request, "Project or Task Category not found")
        return redirect(reverse("projectsapp:projects"))

    if not user.is_admin_in_project(project):
        messages.error(request, "You are not authorized to perform this action")
        return redirect(reverse("projectsapp:projects"))

    return render(
        request,
        "manage_task_category.html",
        {
            "project": project,
            "task_category": task_category,
            "add_user_form": add_user_to_category_form(task_category),
            "add_task_form": add_task_to_category_form(task_category),
        },
    )


@login_required
def create_task_category(request, project_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)

    if not project:
        messages.error(request, "Project not found")
        return redirect(reverse("projectsapp:projects"))

    if not user.is_admin_in_project(project):
        messages.error(request, "You are not authorized to perform this action")
        return redirect(reverse("projectsapp:projects"))

    new_task_category = TaskCategory(
        name="New Task Category", project=project, repo=repo
    )

    repo.insert_task_category(new_task_category)

    return redirect(
        f"{reverse('projectsapp:manage_task_category', args=[project_id, new_task_category.id])}?no_fade=False"
    )


@login_required
def delete_task_category(request, project_id: UUID, category_id: UUID):
    user = authenticate(request)
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    task_category = repo.get_task_category_by_id(category_id)

    if not project or not task_category:
        messages.error(request, "Project or Task Category not found")
        return redirect(reverse("projectsapp:projects"))

    if not user.is_admin_in_project(project):
        messages.error(request, "You are not authorized to perform this action")
        return redirect(reverse("projectsapp:projects"))

    if request.method == "POST":
        try:
            repo.delete_task_category(task_category)
            messages.success(request, "Category deleted successfully")
            return redirect(
                f"{reverse('projectsapp:manage_project', args=[project_id])}?no_fade=True"
            )
        except Exception as e:
            messages.error(request, f"Error deleting category: {str(e)}")

    return redirect(
        f"{reverse('projectsapp:manage_task_category', args=[project_id, category_id])}?no_fade=True"
    )


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = old_authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("projectsapp:projects")
            else:
                form.add_error(None, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


@login_required
def user_logout(request):
    logout(request)
    return redirect("home")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projectsapp:projects")
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})


@login_required
def auto_assign_tasks(request, project_id: UUID):
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    if project is None:
        return HttpResponseNotFound("Project not found")

    if not request.user.as_entity(repo).is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    auto_assigner = AutoTaskAssigner(repo, project)
    auto_assigner.auto_assign_tasks()
    messages.success(request, "Successfully assigned tasks")
    return redirect(
        f"{reverse('projectsapp:manage_project', args=[project_id])}?no_fade=True"
    )
