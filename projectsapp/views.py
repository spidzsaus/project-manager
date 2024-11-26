from uuid import UUID

from django.shortcuts import render

from projectsapp.repo import Repo
from projectsapp.entities.users import User
from projectsapp.entities.projects import Project


def home(request):
    return render(request, "home.html")


def index(request):
    """
    Тестовая страница, которая выводит карточки со всеми проектами, частью которых является
    тестовый пользователь.
    """

    repo = Repo()  # Создание объекта класса Repo для доступа к БД
    test_id = UUID(
        "00000000-0000-0000-0000-000000000000"
    )  # Идентификатор тестового пользователя

    test_user = repo.get_user_by_id(
        test_id
    )  # Получение тестового пользователя из базы данных

    # Если тестового пользователя нет в базе данных, то создаем его,
    # а так же создаём первый тестовый проект (чисто для теста :P)
    if not test_user:
        # Создание нового оъекта класса User.
        test_user = User(id=test_id, name="test_user", repo=Repo())

        # Сохранение нового пользователя в базе данных
        repo.insert_user(test_user)

        # Создание нового объекта класса Project
        test_project = Project(id=test_id, name="test_project", repo=Repo())

        # Сохранение нового проекта в базе данных
        repo.insert_project(test_project)

        # Добавление пользователя в проект
        repo.add_user_to_project(test_user, test_project)

    # Получение всех проектов, в которых участвует тестовый пользователь
    projects_list = test_user.get_projects()

    # Возвращаем страницу с карточками проектов.
    # Страница генерируется на основе шаблона test.html
    # с подстановкой списка проектов в параметр projects_list
    return render(request, "test.html", {"projects_list": projects_list})
