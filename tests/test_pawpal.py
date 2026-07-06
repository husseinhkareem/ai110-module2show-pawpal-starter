"""Pytest suite for PawPal+ core behaviors: completion, adding, sorting, recurrence, conflicts."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def _owner_with_pet() -> tuple[Owner, Pet]:
    """Helper: build an owner with a single pet."""
    pet = Pet("Buddy", "dog")
    owner = Owner("Ali", [pet])
    return owner, pet


def test_mark_complete():
    """Completing a task flips completed from False to True."""
    task = Task("Walk", "Buddy", date.today(), "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    """Adding a task raises the pet's task count by exactly one."""
    pet = Pet("Buddy", "dog")
    assert len(pet.list_tasks()) == 0
    pet.add_task(Task("Walk", "Buddy", date.today(), "08:00"))
    assert len(pet.list_tasks()) == 1


def test_sort_by_time():
    """Tasks added out of order come back in chronological (date, time) order."""
    owner, pet = _owner_with_pet()
    today = date.today()
    pet.add_task(Task("Evening", "Buddy", today, "18:00"))
    pet.add_task(Task("Morning", "Buddy", today, "08:00"))
    pet.add_task(Task("Noon", "Buddy", today, "12:00"))
    times = [t.due_time for t in Scheduler(owner).sort_by_time()]
    assert times == ["08:00", "12:00", "18:00"]


def test_recurrence_creates_next_day():
    """Completing a daily task adds a new task dated today+1 with completed=False."""
    owner, pet = _owner_with_pet()
    today = date.today()
    daily = Task("Walk", "Buddy", today, "08:00", frequency="daily")
    pet.add_task(daily)
    new_task = Scheduler(owner).mark_task_complete(daily)
    assert new_task is not None
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.completed is False
    assert new_task in pet.list_tasks()


def test_conflict_detection():
    """Two incomplete tasks at the same date/time warn; distinct times do not."""
    owner, pet = _owner_with_pet()
    today = date.today()
    pet.add_task(Task("Vet", "Buddy", today, "09:00"))
    pet.add_task(Task("Grooming", "Buddy", today, "09:00"))
    assert Scheduler(owner).detect_conflicts()  # non-empty

    owner2, pet2 = _owner_with_pet()
    pet2.add_task(Task("Vet", "Buddy", today, "09:00"))
    pet2.add_task(Task("Grooming", "Buddy", today, "10:00"))
    assert Scheduler(owner2).detect_conflicts() == []
