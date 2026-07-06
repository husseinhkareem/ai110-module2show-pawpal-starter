"""PawPal+ CLI demo: builds a sample owner/pets/tasks and exercises the scheduler."""

from datetime import date

from pawpal_system import (
    Owner,
    Pet,
    Task,
    Scheduler,
    format_schedule,
    save_data,
    load_data,
)


def section(title: str) -> None:
    """Print a labeled section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def build_demo_owner() -> Owner:
    """Create one owner, two pets, and several tasks (times deliberately out of order)."""
    today = date.today()
    owner = Owner("Ali", [])

    buddy = Pet("Buddy", "dog")
    max_cat = Pet("Max", "cat")
    owner.add_pet(buddy)
    owner.add_pet(max_cat)

    # Times added out of order on purpose to prove sorting works.
    buddy.add_task(Task("Evening walk", "Buddy", today, "18:00", "daily", priority=2))
    buddy.add_task(Task("Morning walk", "Buddy", today, "08:00", "daily", priority=1))
    buddy.add_task(Task("Vet visit", "Buddy", today, "09:00", "once", priority=1))
    max_cat.add_task(Task("Grooming", "Max", today, "09:00", "weekly", priority=2))
    max_cat.add_task(Task("Feeding", "Max", today, "08:15", "daily", priority=1))
    return owner


def main() -> None:
    """Run the full PawPal+ CLI demonstration."""
    owner = build_demo_owner()
    scheduler = Scheduler(owner)

    print(f"PawPal+ daily planner for {owner.name} "
          f"({len(owner.list_pets())} pets, {len(owner.all_tasks())} tasks) — {date.today()}")

    section("1. Today's schedule, sorted by time")
    print(format_schedule(scheduler.sort_by_time(scheduler.todays_schedule())))

    section("2. Sorted by priority (1=high, 2=medium, 3=low)")
    print(format_schedule(scheduler.sort_by_priority()))

    section("3a. Filter by pet: Buddy")
    print(format_schedule(scheduler.filter_by_pet("Buddy")))

    section("3b. Filter by status: incomplete tasks")
    print(format_schedule(scheduler.filter_by_status(False)))

    section("4a. Conflict warnings (same exact date + time)")
    conflicts = scheduler.detect_conflicts()
    print("\n".join(conflicts) if conflicts else "No conflicts.")

    section("4b. Overlap warnings (30-min time blocks)")
    overlaps = scheduler.detect_overlaps(duration_minutes=30)
    print("\n".join(overlaps) if overlaps else "No overlaps.")

    section("5. Next available 30-min slot today")
    print(scheduler.next_available_slot(duration_minutes=30))

    section("6. Recurrence proof: complete Buddy's daily 'Morning walk'")
    morning_walk = next(
        t for t in owner.all_tasks()
        if t.description == "Morning walk" and t.pet_name == "Buddy"
    )
    new_task = scheduler.mark_task_complete(morning_walk)
    if new_task is not None:
        print(f"Completed: {morning_walk}")
        print(f"Auto-generated next occurrence: {new_task} (due {new_task.due_date})")
    print("\nSchedule after completion (note the new task tomorrow + the ✅):")
    print(format_schedule(scheduler.sort_by_time()))

    section("7. Persistence proof: save then reload")
    save_data(owner)
    reloaded = load_data()
    if reloaded is not None:
        print(f"Saved to pawpal_data.json and reloaded owner '{reloaded.name}' "
              f"with {len(reloaded.all_tasks())} tasks across {len(reloaded.list_pets())} pets.")


if __name__ == "__main__":
    main()
