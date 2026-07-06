"""PawPal+ logic layer: data models, scheduling algorithms, and JSON persistence.

Scheduling algorithms implemented (sort/filter/conflict/overlap/recurrence).
Priority sort, next-available-slot, persistence, and formatting land next.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


PRIORITY_LABELS = {1: "high", 2: "medium", 3: "low"}


def _time_to_minutes(hhmm: str) -> int:
    """Convert an 'HH:MM' string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


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
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Return the next recurring Task, or None if this task is one-off."""
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(days=7)
        else:
            return None
        return Task(
            description=self.description,
            pet_name=self.pet_name,
            due_date=self.due_date + delta,
            due_time=self.due_time,
            frequency=self.frequency,
            completed=False,
            priority=self.priority,
        )

    def __str__(self) -> str:
        """Readable one-line summary of the task."""
        status = "✅" if self.completed else "⬜"
        return f"⏰ {self.due_time} | {self.pet_name} | {self.description} | {self.frequency} | {status}"


@dataclass
class Pet:
    """A pet owned by the user, holding its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return self.tasks

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet if present."""
        if task in self.tasks:
            self.tasks.remove(task)


class Owner:
    """The pet owner; holds pets and aggregates tasks across all of them."""

    def __init__(self, name: str, pets: "list[Pet] | None" = None) -> None:
        """Create an owner with a name and optional starting list of pets."""
        self.name = name
        self.pets: list[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> "Pet | None":
        """Return the pet with the given name, or None."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def list_pets(self) -> list[Pet]:
        """Return all pets."""
        return self.pets

    def all_tasks(self) -> list[Task]:
        """Return a flat list of every task across every pet (cross-pet aggregation)."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Scheduler:
    """Reads an Owner's tasks and provides sorting, filtering, and conflict logic."""

    def __init__(self, owner: Owner) -> None:
        """Bind the scheduler to an owner."""
        self.owner = owner

    def sort_by_time(self, tasks: "list[Task] | None" = None) -> list[Task]:
        """Return tasks sorted by (due_date, due_time); defaults to all tasks."""
        if tasks is None:
            tasks = self.owner.all_tasks()
        return sorted(tasks, key=lambda t: (t.due_date, t.due_time))

    def todays_schedule(self) -> list[Task]:
        """Return today's tasks sorted by time."""
        today = date.today()
        todays = [t for t in self.owner.all_tasks() if t.due_date == today]
        return self.sort_by_time(todays)

    def filter_by_pet(self, name: str) -> list[Task]:
        """Return all tasks belonging to the named pet."""
        return [t for t in self.owner.all_tasks() if t.pet_name == name]

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return all tasks matching the given completion state."""
        return [t for t in self.owner.all_tasks() if t.completed == completed]

    def detect_conflicts(self) -> list[str]:
        """Warn about incomplete tasks sharing the same date and time (across all pets)."""
        groups: dict[tuple, list[Task]] = {}
        for t in self.owner.all_tasks():
            if t.completed:
                continue
            groups.setdefault((t.due_date, t.due_time), []).append(t)
        warnings: list[str] = []
        for (due, tm), group in groups.items():
            if len(group) >= 2:
                names = " & ".join(f"{t.pet_name} ({t.description})" for t in group)
                warnings.append(f"⚠️ Conflict at {tm} on {due.isoformat()}: {names}")
        return warnings

    def mark_task_complete(self, task: Task) -> "Task | None":
        """Complete a task; if recurring, generate and attach the next occurrence."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is None:
            return None
        pet = self.owner.get_pet(task.pet_name)
        if pet is not None:
            pet.add_task(next_task)
        return next_task

    def detect_overlaps(self, duration_minutes: int = 30) -> list[str]:
        """Warn about incomplete tasks whose [start, start+duration] blocks overlap."""
        incomplete = [t for t in self.owner.all_tasks() if not t.completed]
        warnings: list[str] = []
        for i in range(len(incomplete)):
            for j in range(i + 1, len(incomplete)):
                a, b = incomplete[i], incomplete[j]
                if a.due_date != b.due_date:
                    continue
                a_start = _time_to_minutes(a.due_time)
                b_start = _time_to_minutes(b.due_time)
                if a_start < b_start + duration_minutes and b_start < a_start + duration_minutes:
                    warnings.append(
                        f"⚠️ Overlap on {a.due_date.isoformat()}: "
                        f"{a.pet_name} ({a.description}) at {a.due_time} "
                        f"overlaps {b.pet_name} ({b.description}) at {b.due_time}"
                    )
        return warnings

    def sort_by_priority(self, tasks: "list[Task] | None" = None) -> list[Task]:
        """Return tasks sorted by (priority, due_date, due_time)."""
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
