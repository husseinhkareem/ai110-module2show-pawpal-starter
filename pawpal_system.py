"""PawPal+ logic layer: data models, scheduling algorithms, and JSON persistence.

Skeleton phase: class shapes and method signatures only. Bodies raise
NotImplementedError until the logic is implemented in later commits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


PRIORITY_LABELS = {1: "high", 2: "medium", 3: "low"}


@dataclass
class Task:
    """A single care task for a pet, due at a specific date and HH:MM time."""

    description: str
    pet_name: str
    due_date: date
    due_time: str
    frequency: str = "once"
    completed: bool = False
    priority: int = 2

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError

    def next_occurrence(self) -> "Task | None":
        """Return the next recurring Task, or None if this task is one-off."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Readable one-line summary of the task."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet owned by the user, holding its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet if present."""
        raise NotImplementedError


class Owner:
    """The pet owner; holds pets and aggregates tasks across all of them."""

    def __init__(self, name: str, pets: "list[Pet] | None" = None) -> None:
        """Create an owner with a name and optional starting list of pets."""
        self.name = name
        self.pets: list[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def get_pet(self, name: str) -> "Pet | None":
        """Return the pet with the given name, or None."""
        raise NotImplementedError

    def list_pets(self) -> list[Pet]:
        """Return all pets."""
        raise NotImplementedError

    def all_tasks(self) -> list[Task]:
        """Return a flat list of every task across every pet (cross-pet aggregation)."""
        raise NotImplementedError


class Scheduler:
    """Reads an Owner's tasks and provides sorting, filtering, and conflict logic."""

    def __init__(self, owner: Owner) -> None:
        """Bind the scheduler to an owner."""
        self.owner = owner

    def sort_by_time(self, tasks: "list[Task] | None" = None) -> list[Task]:
        """Return tasks sorted by (due_date, due_time); defaults to all tasks."""
        raise NotImplementedError

    def todays_schedule(self) -> list[Task]:
        """Return today's tasks sorted by time."""
        raise NotImplementedError

    def filter_by_pet(self, name: str) -> list[Task]:
        """Return all tasks belonging to the named pet."""
        raise NotImplementedError

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return all tasks matching the given completion state."""
        raise NotImplementedError

    def detect_conflicts(self) -> list[str]:
        """Warn about incomplete tasks sharing the same date and time."""
        raise NotImplementedError

    def mark_task_complete(self, task: Task) -> "Task | None":
        """Complete a task; if recurring, generate and attach the next occurrence."""
        raise NotImplementedError

    def sort_by_priority(self, tasks: "list[Task] | None" = None) -> list[Task]:
        """Return tasks sorted by (priority, due_date, due_time)."""
        raise NotImplementedError

    def detect_overlaps(self, duration_minutes: int = 30) -> list[str]:
        """Warn about incomplete tasks whose duration blocks overlap."""
        raise NotImplementedError

    def next_available_slot(
        self,
        day: "date | None" = None,
        duration_minutes: int = 30,
        day_start: str = "08:00",
        day_end: str = "20:00",
    ) -> str:
        """Return the first free HH:MM start that fits duration, or a no-slot message."""
        raise NotImplementedError


def save_data(owner: Owner, path: str = "pawpal_data.json") -> None:
    """Serialize an owner (with pets and tasks) to JSON on disk."""
    raise NotImplementedError


def load_data(path: str = "pawpal_data.json") -> "Owner | None":
    """Load an owner from JSON, or return None if the file is missing."""
    raise NotImplementedError


def format_schedule(tasks: list[Task]) -> str:
    """Return a tabulate grid of tasks (Time, Pet, Task, Freq, Priority, Done)."""
    raise NotImplementedError
