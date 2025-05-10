from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from projectsapp.entities import IDComparable

if TYPE_CHECKING:
    from projectsapp.entities.projects import Project
    from projectsapp.entities.tasks import Task
    from projectsapp.entities.users import User
    from projectsapp.repo import Repo


@dataclass(eq=False)
class JournalRecord(IDComparable):
    class EventType(Enum):
        ASSIGN_TASK_TO_USER = 0
        UNASSIGN_TASK_FROM_USER = 1
        SET_IN_PROCESS = 2
        SET_DONE = 3
        SET_TODO = 4
        ADD_USER_TO_PROJECT = 5
        PROMOTE_USER_IN_PROJECT = 6

    user: User | None
    task: Task | None
    project: Project | None
    event_type: EventType
    repo: Repo

    id: UUID = field(default_factory=uuid4)
    date: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @property
    def event_type_display(self):
        return self.event_type.name
