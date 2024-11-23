from uuid import UUID

from django.shortcuts import render

from projectsapp.repo import Repo
from projectsapp.entities.users import User
from projectsapp.entities.projects import Project

def home(request):
    return render(request, 'home.html')

def index(request):
    '''
    Тестовая страница, которая выводит карточки со всеми проектами, частью которых является
    тестовый пользователь.
    '''

    repo = Repo()
    test_id = UUID('00000000-0000-0000-0000-000000000000')

    test_user = repo.get_user_by_id(test_id)
    if not test_user:
        test_user = User(id=test_id, name='test_user', repo=Repo())
        repo.insert_user(test_user)

        test_project = Project(id=test_id, name='test_project', repo=Repo())
        repo.insert_project(test_project)

        repo.add_user_to_project(test_user, test_project)

    return render(request, 'test.html', {'projects_list': test_user.get_projects()})