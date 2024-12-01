from uuid import UUID

from django.shortcuts import render, redirect

from projectsapp.repo import Repo
from projectsapp.entities.users import User
from projectsapp.entities.projects import Project
from projectsapp.entities.tasks import Task

from projectsapp.forms import CreateProjectForm

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
    return render(request, "test.html", {"projects_list": projects_list})

def index(request):
    return render(request, "index.html")