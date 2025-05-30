from projectsapp.entities.projects import Project
from projectsapp.repo import Repo


class AutoTaskAssigner:
    repo: Repo
    project: Project

    def __init__(self, repo: Repo, project: Project):
        self.repo = repo
        self.project = project

    def auto_assign_tasks(self):
        all_tasks = self.repo.get_unassigned_tasks(self.project)
        all_tasks = sorted(
            all_tasks, key=lambda x: self.repo.count_tasks_dependant_on(self.project, x)
        )
        for task in all_tasks:
            suitable_users = task.get_users_suitable_for_task()

            suitable_users = sorted(
                suitable_users,
                key=lambda x: self.repo.count_member_assignments(self.project, x),
            )

            task.assign_user(suitable_users[0])
