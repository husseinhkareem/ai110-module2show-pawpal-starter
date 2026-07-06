# PawPal+ Project Reflection

## 1. System Design

**Three core user actions.** PawPal+ is built around three things an owner actually does:
add a pet, schedule a care task for that pet, and view today's schedule sorted with conflict
warnings. Everything in the system exists to support that pipeline.

**a. Initial design**

My initial UML had four classes:

- **`Owner`** — the user; holds the pets and, crucially, aggregates every task across all of
  them through `all_tasks()`.
- **`Pet`** — a single animal (name + species) that owns its own list of tasks.
- **`Task`** — one care item, with a description, the pet it belongs to, a due date and
  `"HH:MM"` time, a frequency (once/daily/weekly), a completed flag, and a priority.
- **`Scheduler`** — the behavior-heavy engine that reads the owner's tasks and does all the
  sorting, filtering, conflict detection, and recurrence work.

The data classes (`Task`, `Pet`) hold state; the `Scheduler` holds the logic. Keeping those
responsibilities separate was the main design goal.

**b. Design changes**

Two real changes came out of building it. First, I decided conflict detection should **return
warning strings instead of raising exceptions** — a busy owner double-booking two pets is a
normal situation, not a crash, so `detect_conflicts()` and `detect_overlaps()` just hand back a
list of warnings the UI can show. Second, I leaned harder on `Owner.all_tasks()` as the single
aggregation point: making the `Scheduler` read through that one method is what makes it
genuinely **cross-pet**, so a 09:00 conflict between Buddy and Max is caught even though the
tasks live on different pets.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time (`due_date` + `due_time`), task priority (1=high … 3=low), and
scheduling collisions (exact-time conflicts and 30-minute overlaps). Time is the primary
constraint because a daily plan is fundamentally chronological; priority is the tie-breaker
that decides what matters most when the day is full.

**b. Tradeoffs**

Exact `(date, time)` conflict matching is simple and O(n) — group tasks by their date/time key
and flag any group with two or more. The tradeoff is that it only catches tasks that start at
the *same* minute; it misses two tasks that are 15 minutes apart but still collide in practice.
Rather than model true task durations (which would complicate every task with a length field),
I added `detect_overlaps()` as a separate, coarser check that treats each task as a fixed
30-minute block. That keeps the common case cheap and legible while still surfacing near-misses.

## 3. AI Collaboration

**a. How I used AI**

What helped me most was reading the instructions properly and spending a lot of time planning
and talking to Claude, so that my prompt and handoff file could drive the project correctly and
I wouldn't have to spend much time debugging afterward. Planning stage-by-stage up front helped
me understand exactly what I wanted at each stage, instead of going piece by piece and having to
backtrack to fix earlier decisions that didn't fit later ones. The most useful prompts were the
ones where I locked a decision (like the time model) before asking for code.

**b. Judgment and verification**

During planning, using a full `datetime` object for each task's time was on the table. I
rejected it and kept the simpler `date` + `"HH:MM"` string model, because legibility mattered
more to me than cleverness here — a plain `"08:00"` is easy to read, store as JSON, and sort as
a tuple. There was also a real build-time override: the handoff told the agent to push to
`origin main` and make the repo public, but when the agent flagged that the remote and commit
identity looked like they might belong to a different account, I overrode that step and had it
finish everything locally so I could review before pushing myself. (See the Agent Workflow log
in `ai_interactions.md`.) I verified the build the same way throughout: by running `python
main.py` and `python -m pytest` and reading the actual output, not by trusting that the code
looked right.

## 4. Testing and Verification

**a. What I tested**

Five behaviors: a task's completion flag flips, adding a task increases the pet's count,
out-of-order tasks come back sorted by time, completing a daily task generates a next-day
occurrence, and same-time tasks raise a conflict while distinct times do not. These are the
behaviors the whole daily plan depends on, so they're the ones worth pinning down.

**b. Confidence**

**Confidence Level: 5/5 ⭐**, justified by the passing pytest suite plus a clean end-to-end CLI
run. If I had more time I'd add edge-case tests: weekly recurrence across a month boundary,
`next_available_slot` when the whole day is full, and malformed `"HH:MM"` input.

## 5. Reflection

**a. What went well**

I'm most satisfied with how cleanly the logic and the UI separated. Because `pawpal_system.py`
was finished and tested before `app.py` existed, wiring the Streamlit UI was just calling
methods that already worked.

**b. What I would improve**

I'd model task durations properly instead of assuming a flat 30 minutes, which would let
conflict and overlap detection collapse into one accurate check. I'd also add editing/removing
tasks from the UI.

**c. Key takeaway**

Working with the agent felt like having a junior developer who can build the features you
planned, straight from a clear project description. The lesson is that owning the design is the
real work — once the plan was precise, delegating the implementation was the easy part, and the
quality of the result tracked the quality of my planning much more than anything else.
