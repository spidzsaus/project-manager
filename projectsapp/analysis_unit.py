from datetime import datetime, timedelta

from projectsapp.entities.projects import Project
from projectsapp.entities.tasks import Task
from projectsapp.entities.users import User
from projectsapp.entities.records import JournalRecord
from projectsapp.repo import Repo


class AnalysisUnit:
    project: Project

    def __init__(self, project: Project) -> None:
        self.project = project

    def _metrics(self, today: datetime) -> tuple[dict, int, int, int]:
        repo = self.project.repo

        total_tasks = repo.count_tasks_in_project(self.project)
        completed_tasks = repo.count_completed_tasks_in_project(self.project)
        active_tasks = repo.count_active_tasks_in_project(self.project)
        delayed_tasks = repo.count_delayed_tasks_in_project(self.project, today)
        not_started_tasks = repo.count_not_started_tasks_in_project(self.project)

        completed_tasks_with_duration = []
        for task in repo.get_complete_tasks(self.project):
            start_date = task.get_start_date()
            finish_date = task.get_finish_date()
            if start_date and finish_date and finish_date > start_date:
                duration = (finish_date - start_date).days
                completed_tasks_with_duration.append(
                    {"task_id": task.id, "duration": duration}
                )

        avg_duration = 0
        if completed_tasks_with_duration:
            total_duration = sum(
                task["duration"] for task in completed_tasks_with_duration
            )
            avg_duration = total_duration / len(completed_tasks_with_duration)

        return (
            {
                "completion_rate": round(
                    (completed_tasks / total_tasks * 100) if total_tasks else 0, 1
                ),
                "active_tasks": active_tasks,
                "avg_task_duration": round(avg_duration, 1),
                "team_members": repo.count_team_members(self.project),
                "active_members": repo.count_busy_members(self.project),
                "on_time_rate": (
                    round((completed_tasks - delayed_tasks) / completed_tasks * 100, 1)
                    if completed_tasks
                    else 0
                ),
                "delayed_tasks": delayed_tasks,
            },
            completed_tasks,
            active_tasks,
            not_started_tasks,
        )

    def _completion_trend(self, today: datetime) -> dict:
        completion_trend = {"labels": [], "data": []}
        cumulative_completed = 0

        for i in range(4, 0, -1):
            week_start = today - timedelta(weeks=i)
            week_end = week_start + timedelta(weeks=1)

            week_completed = self.project.repo.count_completed_tasks_in_date_range(
                self.project, week_start, week_end
            )

            cumulative_completed += week_completed
            completion_trend["labels"].append(f"Week {5-i}")
            completion_trend["data"].append(cumulative_completed)

        return completion_trend

    def _team_perfomance(self, today: datetime) -> list:
        team_performance = []

        repo = self.project.repo

        members = self.project.repo.get_data_rich_members(self.project, today)

        for member in members:
            assigned = member.assigned_tasks or 0  # type: ignore
            completed = member.completed_tasks or 0  # type: ignore
            in_progress = member.in_progress_tasks or 0  # type: ignore
            delayed = member.delayed_tasks or 0  # type: ignore

            completion_rate = round((completed / assigned * 100) if assigned else 0, 1)
            on_time_rate = round(
                ((completed - delayed) / completed * 100) if completed else 0, 1
            )

            # Calculate average completion time for member's completed tasks
            member_avg_duration = 0
            member_tasks = repo.get_tasks_completed_by_user(
                self.project, member.as_entity(repo)
            )

            task_durations = []
            for task in member_tasks:
                start_record = repo.get_start_record_for_task(task)

                end_record = repo.get_finish_record_for_task(task)

                if start_record and end_record and end_record.date > start_record.date:
                    duration = (end_record.date - start_record.date).days
                    task_durations.append(duration)

            if task_durations:
                member_avg_duration = sum(task_durations) / len(task_durations)

            # Efficiency calculation
            efficiency = min(
                100,
                max(
                    0, completion_rate * 0.8 + (100 - (member_avg_duration or 0)) * 0.2
                ),
            )

            team_performance.append(
                {
                    "id": str(member.id),
                    "name": member.username,
                    "assigned_tasks": assigned,
                    "completed_tasks": completed,
                    "in_progress_tasks": in_progress,
                    "completion_rate": completion_rate,
                    "on_time_rate": on_time_rate,
                    "avg_completion_time": round(member_avg_duration, 1),
                    "efficiency": round(efficiency, 1),
                    "task_volume": min(100, assigned * 10),
                    "collaboration": min(
                        100, (repo.count_team_members(self.project) / 5) * efficiency
                    ),
                }
            )

        return team_performance

    def _dependencies_data(self) -> list:
        task_dependencies = []

        repo = self.project.repo

        dependencies = repo.get_data_rich_dependencies(self.project)

        for dep in dependencies:
            task_dependencies.append(
                {
                    "from": str(dep.task.id),
                    "from_name": dep.task.name,
                    "to": str(dep.depends_on.id),
                    "to_name": dep.depends_on.name,
                }
            )
        return task_dependencies

    def _timeline_data(self) -> list:
        timeline_data = []
        for task in self.project.get_tasks():
            start_date = task.get_start_date()
            finish_date = task.get_finish_date()
            assignee = next(iter(task.get_users()), None)
            if start_date and finish_date:
                timeline_data.append(
                    {
                        "x": task.name,
                        "y": [
                            # Convert to milliseconds (*1000)
                            int(start_date.timestamp() * 1000),
                            int(finish_date.timestamp() * 1000),
                        ],
                        "status": task.status.name,
                        "assigned_to": (assignee.name if assignee else "Unassigned"),
                        "duration": (finish_date - start_date).days,
                    }
                )
        return timeline_data

    def cook_data(self) -> dict:

        today = datetime.now()
        metrics, completed, in_progress, not_started = self._metrics(today=today)
        return {
            "metrics": metrics,
            "task_distribution": {
                "completed": completed,
                "in_progress": in_progress,  # In-progress tasks count
                "not_started": not_started,  # Not started tasks count
            },
            "completion_trend": self._completion_trend(today=today),
            "team_performance": self._team_perfomance(today=today),
            "timeline_data": self._timeline_data(),
            "task_dependencies": self._dependencies_data(),
        }
