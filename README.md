# 🐾 PawPal+ (Module 2 Project)

PawPal+ is a smart pet-care management system. It helps a busy pet owner plan care
tasks (walks, feeding, meds, grooming, enrichment) across **multiple pets**, then uses
scheduling logic to organize and prioritize those tasks into a daily plan. It also tries
to explain why it picked that plan.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, grooming, etc.)
- Consider constraints (time available, priority, exact-time conflicts, overlaps)
- Produce a daily plan sorted by time or priority, and warn about scheduling problems

The project is **CLI-first**: the logic layer in `pawpal_system.py` is complete and verified
via `main.py` and `pytest` before the Streamlit UI (`app.py`) is wired to it.

## System & Classes

| Class | Responsibility |
|-------|----------------|
| **`Task`** (`@dataclass`) | One care task: description, owning `pet_name`, `due_date` (a `date`), `due_time` (`"HH:MM"`), `frequency` (`once`/`daily`/`weekly`), `completed`, `priority` (1=high, 2=medium, 3=low). Knows how to `mark_complete()` and produce its `next_occurrence()`. |
| **`Pet`** (`@dataclass`) | A pet (`name`, `species`) that owns a list of `Task`s; can `add_task`, `list_tasks`, `remove_task`. |
| **`Owner`** | The user (`name`) who owns many `Pet`s. `all_tasks()` flattens every task across every pet, and that is what lets the `Scheduler` work **across pets**. |
| **`Scheduler`** | The behavior-heavy engine. Constructed with an `Owner` and reads through `owner.all_tasks()` to sort, filter, detect conflicts/overlaps, complete recurring tasks, and find open slots. |

**Relationships:** `Owner "1" o-- "*" Pet`, `Pet "1" o-- "*" Task`, `Scheduler ..> Owner` (reads).

## Features

- **Sort by time**: orders tasks by `(due_date, due_time)`.
- **Priority sorting**: puts high-priority tasks first using `(priority, due_date, due_time)`.
- **Filter by pet** and **filter by completion status**.
- **Exact-time conflict detection**: flags incomplete tasks that share the same date and time (across pets).
- **Duration overlap detection**: flags incomplete tasks whose 30-minute blocks overlap even when the start times differ.
- **Daily/weekly recurrence**: completing a recurring task makes the next one automatically.
- **Next-available-slot**: finds the first free time block in the day.
- **JSON persistence**: saves and loads the full owner, pets, and tasks tree.
- **tabulate + emoji formatting**: schedule grids with ✅/⬜ status.

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by time | `Scheduler.sort_by_time()` | `sorted(key=(due_date, due_time))` |
| Priority sort | `Scheduler.sort_by_priority()` | key `(priority, due_date, due_time)` |
| Filtering | `Scheduler.filter_by_pet()` / `Scheduler.filter_by_status()` | by pet name / completion state |
| Conflict handling | `Scheduler.detect_conflicts()` | exact `(date, time)` match → warning strings |
| Overlap handling | `Scheduler.detect_overlaps()` | 30-min time-block overlap → warning strings |
| Recurring tasks | `Task.next_occurrence()` + `Scheduler.mark_task_complete()` | daily = +1 day, weekly = +7 days |
| Next free slot | `Scheduler.next_available_slot()` | first gap fitting the duration before day end |
| Persistence | `save_data()` / `load_data()` | JSON; dates via `date.isoformat()` / `fromisoformat` |

## Running the demo

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Real captured output from `python main.py`:

```text
PawPal+ daily planner for Ali (2 pets, 5 tasks) — 2026-07-06

============================================================
1. Today's schedule, sorted by time
============================================================
| Time   | Pet   | Task         | Freq   | Priority   | Done   |
|--------|-------|--------------|--------|------------|--------|
| 08:00  | Buddy | Morning walk | daily  | high       | ⬜     |
| 08:15  | Max   | Feeding      | daily  | high       | ⬜     |
| 09:00  | Buddy | Vet visit    | once   | high       | ⬜     |
| 09:00  | Max   | Grooming     | weekly | medium     | ⬜     |
| 18:00  | Buddy | Evening walk | daily  | medium     | ⬜     |

============================================================
2. Sorted by priority (1=high, 2=medium, 3=low)
============================================================
| Time   | Pet   | Task         | Freq   | Priority   | Done   |
|--------|-------|--------------|--------|------------|--------|
| 08:00  | Buddy | Morning walk | daily  | high       | ⬜     |
| 08:15  | Max   | Feeding      | daily  | high       | ⬜     |
| 09:00  | Buddy | Vet visit    | once   | high       | ⬜     |
| 09:00  | Max   | Grooming     | weekly | medium     | ⬜     |
| 18:00  | Buddy | Evening walk | daily  | medium     | ⬜     |

============================================================
3a. Filter by pet: Buddy
============================================================
| Time   | Pet   | Task         | Freq   | Priority   | Done   |
|--------|-------|--------------|--------|------------|--------|
| 18:00  | Buddy | Evening walk | daily  | medium     | ⬜     |
| 08:00  | Buddy | Morning walk | daily  | high       | ⬜     |
| 09:00  | Buddy | Vet visit    | once   | high       | ⬜     |

============================================================
3b. Filter by status: incomplete tasks
============================================================
| Time   | Pet   | Task         | Freq   | Priority   | Done   |
|--------|-------|--------------|--------|------------|--------|
| 18:00  | Buddy | Evening walk | daily  | medium     | ⬜     |
| 08:00  | Buddy | Morning walk | daily  | high       | ⬜     |
| 09:00  | Buddy | Vet visit    | once   | high       | ⬜     |
| 09:00  | Max   | Grooming     | weekly | medium     | ⬜     |
| 08:15  | Max   | Feeding      | daily  | high       | ⬜     |

============================================================
4a. Conflict warnings (same exact date + time)
============================================================
⚠️ Conflict at 09:00 on 2026-07-06: Buddy (Vet visit) & Max (Grooming)

============================================================
4b. Overlap warnings (30-min time blocks)
============================================================
⚠️ Overlap on 2026-07-06: Buddy (Morning walk) at 08:00 overlaps Max (Feeding) at 08:15
⚠️ Overlap on 2026-07-06: Buddy (Vet visit) at 09:00 overlaps Max (Grooming) at 09:00

============================================================
5. Next available 30-min slot today
============================================================
09:30

============================================================
6. Recurrence proof: complete Buddy's daily 'Morning walk'
============================================================
Completed: ⏰ 08:00 | Buddy | Morning walk | daily | ✅
Auto-generated next occurrence: ⏰ 08:00 | Buddy | Morning walk | daily | ⬜ (due 2026-07-07)

Schedule after completion (note the new task tomorrow + the ✅):
| Time   | Pet   | Task         | Freq   | Priority   | Done   |
|--------|-------|--------------|--------|------------|--------|
| 08:00  | Buddy | Morning walk | daily  | high       | ✅     |
| 08:15  | Max   | Feeding      | daily  | high       | ⬜     |
| 09:00  | Buddy | Vet visit    | once   | high       | ⬜     |
| 09:00  | Max   | Grooming     | weekly | medium     | ⬜     |
| 18:00  | Buddy | Evening walk | daily  | medium     | ⬜     |
| 08:00  | Buddy | Morning walk | daily  | high       | ⬜     |

============================================================
7. Persistence proof: save then reload
============================================================
Saved to pawpal_data.json and reloaded owner 'Ali' with 6 tasks across 2 pets.
```

## 🧪 Testing PawPal+

```bash
python -m pytest          # or: python -m pytest -v
```

The 5 tests cover the core behaviors: task **completion** flips the flag, **adding** a task
raises the pet's count, **sort-by-time** returns out-of-order tasks chronologically,
**recurrence** creates a next-day task on completing a daily task, and **conflict detection**
warns on same-time tasks but stays silent on distinct times.

Real captured output from `python -m pytest -v`:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.5.0 -- /opt/homebrew/Caskroom/miniconda/base/bin/python3
cachedir: .pytest_cache
rootdir: /Users/asapmoovie/Desktop/codePath/ai110-module2show-pawpal-starter
plugins: anyio-4.7.0
collecting ... collected 5 items

tests/test_pawpal.py::test_mark_complete PASSED                          [ 20%]
tests/test_pawpal.py::test_add_task_increases_count PASSED               [ 40%]
tests/test_pawpal.py::test_sort_by_time PASSED                           [ 60%]
tests/test_pawpal.py::test_recurrence_creates_next_day PASSED            [ 80%]
tests/test_pawpal.py::test_conflict_detection PASSED                     [100%]

============================== 5 passed in 0.01s ===============================
```

**Confidence Level: 5/5 ⭐**. Every core scheduling behavior (completion, aggregation,
sorting, recurrence, conflict detection) is covered by a passing test, and the CLI demo
runs the whole feature set end to end without errors.

## 📸 Demo Walkthrough

PawPal+ can be driven two ways: the Streamlit UI (`streamlit run app.py`) or the CLI (`python main.py`).

**Streamlit UI features:**
1. **Add a pet**: enter a name and species. The pet gets added to the owner and saved to disk.
2. **Schedule a task**: pick a pet, description, date, `HH:MM` time, frequency, and priority. It attaches to that pet and is saved.
3. **Today's schedule**: toggle **By time / By priority**, and filter **by pet** or **by status**. The plan shows up as a table.
4. **Scheduling warnings**: conflicts and overlaps show as `st.warning`s, and the next free 30-minute slot shows in an info panel.

**Example workflow:** add pet *Buddy* (dog) → schedule *Morning walk* at 08:00 daily → view today's schedule → see it sorted alongside Max's tasks, with a 09:00 conflict warning and the next free slot at 09:30.

**Key Scheduler behaviors shown** (from the CLI sample above): time sorting, priority sorting,
per-pet and per-status filtering, exact-time conflict detection, 30-minute overlap detection,
next-available-slot, daily/weekly recurrence, and JSON persistence. See the fenced CLI block
under **Running the demo** for the full run.

## 💾 Data Persistence

State is stored as JSON in `pawpal_data.json`. `save_data(owner)` writes the full
owner, pets, and tasks tree to JSON (dates encoded with `date.isoformat()`); `load_data()` reconstructs
it (parsing dates with `date.fromisoformat`) and returns `None` if the file doesn't exist yet.
Both `pawpal_system.py` (the save/load functions) and `app.py` (which calls `load_data()` once
into `st.session_state` and `save_data()` after every mutation) were built for this workflow, so
pets and tasks survive across app reruns and restarts.

## 🎨 Output Formatting

`format_schedule(tasks)` renders a `tabulate` grid (columns: Time, Pet, Task, Freq, Priority,
Done) with ✅/⬜ emoji status, and preserves the caller's ordering so priority- and time-sorted
views both display correctly. It's used throughout `main.py`; the Streamlit UI renders the same
data via `st.table`. `Task.__str__` gives a compact one-line form (e.g. `⏰ 08:00 | Buddy | Morning walk | daily | ⬜`).
