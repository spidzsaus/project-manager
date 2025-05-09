from uuid import UUID

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse


from projectsapp.entities.projects import Project
from projectsapp.entities.tasks import Task
from projectsapp.entities.users import User
from projectsapp.entities.visitors import ChoicesVisitor
from projectsapp.forms import CreateProjectForm, CreateTaskForm, InviteUserForm
from projectsapp.repo import Repo


def mock_authenticate():
    """
    Фейковая функция аутентификации, возвращает всегда пользователя с ID 00000000-0000-0000-0000-000000000000
    и создаёт его, если такой не найден.
    """

    repo = Repo()  # Создание объекта класса Repo для доступа к БД
    test_id = UUID(
        "00000000-0000-0000-0000-000000000000"
    )  # Идентификатор тестового пользователя

    test_user = repo.get_user_by_id(
        test_id
    )  # Получение тестового пользователя из базы данных

    if not test_user:
        # Создание нового оъекта класса User.
        test_user = User(id=test_id, name="test_user", repo=Repo())

        # Сохранение нового пользователя в базе данных
        repo.insert_user(test_user)

    return test_user


def home(request):
    return render(request, "home.html")


def create_project(request):
    user = mock_authenticate()

    if request.method == "POST":
        form = CreateProjectForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]

            repo = Repo()
            project = Project(name=name, repo=Repo())
            repo.insert_project(project)

            project.add_owner(user)

            return redirect("projectsapp:projects")
    else:
        form = CreateProjectForm()

    return render(request, "create_project.html", {"form": form})


def create_task(request, project_id: UUID):
    user = mock_authenticate()
    repo = Repo()
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


def invite_user(request, project_id: UUID):
    user = mock_authenticate()
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case

    if request.method == "POST":
        form = InviteUserForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]

            repo = Repo()
            user = repo.get_user_by_name(name)
            if not user:
                return HttpResponseNotFound("User not found")

            project.add_user(user)

    return redirect(
        f"{reverse('projectsapp:manage_project', args=[project_id])}?no_fade=True"
    )


def create_task_form(project_id: UUID) -> CreateTaskForm:
    user = mock_authenticate()
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


def invite_user_form(project_id: UUID) -> InviteUserForm:
    user = mock_authenticate()
    repo = Repo()
    project = repo.get_project_by_id(project_id)

    return InviteUserForm()


def project(request, project_id: UUID):
    no_fade = request.GET.get("no_fade") == "True"
    user = mock_authenticate()
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case
    is_admin = user.is_admin_in_project(project)

    tasks_by_statuses = repo.get_tasks_for_user_grouped_by_status(user, project)

    complete_tasks = tasks_by_statuses.get(Task.Status.DONE, [])
    active_tasks = tasks_by_statuses.get(Task.Status.IN_PROCESS, [])
    todo_tasks = tasks_by_statuses.get(Task.Status.TODO, [])

    has_tasks = not not (complete_tasks or active_tasks or todo_tasks)

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
            "user": user,
        },
    )


def manage_project(request, project_id: UUID):
    user = mock_authenticate()
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case

    no_fade = request.GET.get("no_fade") == "True"

    if not user.is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    return render(
        request,
        "manage_project.html",
        {
            "project": project,
            "create_task_form": create_task_form(project_id),
            "no_fade": no_fade,
            "invite_user_form": invite_user_form(project_id),
            "records": project.get_journal_records(),
        },
    )


def projects(request):
    """
    Тестовая страница, которая выводит карточки со всеми проектами, частью которых является
    пользователь.
    """

    user = mock_authenticate()

    # Получение всех проектов, в которых участвует тестовый пользователь
    projects_list = user.get_projects()

    # Возвращаем страницу с карточками проектов.
    # Страница генерируется на основе шаблона test.html
    # с подстановкой списка проектов в параметр projects_list
    return render(request, "projects.html", {"projects_list": projects_list})


def index(request):
    return render(request, "index.html")


def start_task(request, project_id: UUID, task_id: UUID):
    repo = Repo()
    task = repo.get_task_by_id(task_id)
    assert task is not None  # todo: handle this case
    if task.status == Task.Status.TODO:
        task.change_status(Task.Status.IN_PROCESS)
    return redirect(f"{reverse('projectsapp:project', args=[project_id])}?no_fade=True")


def finish_task(request, project_id: UUID, task_id: UUID):
    repo = Repo()
    task = repo.get_task_by_id(task_id)
    assert task is not None  # todo: handle this case
    if task.status == Task.Status.IN_PROCESS:
        task.change_status(Task.Status.DONE)
    return redirect(f"{reverse('projectsapp:project', args=[project_id])}?no_fade=True")


def change_task_status(request, project_id: UUID, task_id: UUID):
    repo = Repo()
    task = repo.get_task_by_id(task_id)
    assert task is not None  # todo: handle this case

    if request.method == "POST":
        status = Task.Status(int(request.POST["status"]))
        task.change_status(status)

    return redirect(f"{reverse('projectsapp:project', args=[project_id])}?no_fade=True")


def delete_task(request, project_id: UUID, task_id: UUID):
    repo = Repo()
    task = repo.get_task_by_id(task_id)
    assert task is not None  # todo: handle this case

    user = mock_authenticate()

    if not user.is_admin_in_project(task.parent_project):
        return HttpResponseForbidden("You are not admin in this project")

    if request.method == "POST":
        repo.delete_task(task)

    return redirect(
        f"{reverse('projectsapp:manage_project', args=[project_id])}?no_fade=True"
    )


def delete_project(request, project_id: UUID):
    repo = Repo()
    project = repo.get_project_by_id(project_id)
    assert project is not None  # todo: handle this case

    user = mock_authenticate()

    if not user.is_admin_in_project(project):
        return HttpResponseForbidden("You are not admin in this project")

    if request.method == "POST":
        repo.delete_project(project)

    return redirect("projectsapp:projects")
