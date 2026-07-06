# PawPal+ Project Reflection

## 1. System Design

**Three core user actions.** There are three things an owner actually does in PawPal+: add a
pet, schedule a care task for a pet, and look at today's schedule with its conflict warnings.
The rest of the app is there to make those three work.

**a. Initial design**

My first UML had four classes:

- **`Owner`**: the user. Holds the pets and pulls together every task across all of them with
  `all_tasks()`.
- **`Pet`**: one animal (name + species) that keeps its own list of tasks.
- **`Task`**: one care item. It has a description, the pet it belongs to, a due date and
  `"HH:MM"` time, a frequency (once/daily/weekly), a completed flag, and a priority.
- **`Scheduler`**: the part that holds the logic. It reads the owner's tasks and does the
  sorting, filtering, conflict detection, and recurrence work.

`Task` and `Pet` just hold data. The `Scheduler` holds the behavior. I wanted those kept apart.

**b. Design changes**

Two things changed while I was building. The first was conflict detection. I made it **return
warning strings instead of raising exceptions**, because a busy owner double-booking two pets
happens all the time and shouldn't crash the app. So `detect_conflicts()` and
`detect_overlaps()` just hand back a list of warnings the UI can show. The second was
`Owner.all_tasks()`. I made the `Scheduler` read everything through that one method, and that is
what lets it work across pets. A 09:00 clash between Buddy and Max gets caught even though the
two tasks sit on different pets.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at time (`due_date` + `due_time`), task priority (1 is high, 3 is low), and
collisions (exact-time conflicts and 30-minute overlaps). Time comes first, since a daily plan
is basically a list in time order. Priority breaks ties. When the day is full, it decides what
shows up first.

**b. Tradeoffs**

Exact `(date, time)` conflict matching is simple and O(n). You group tasks by their date and
time key and flag any group with two or more. The downside is it only catches tasks that start
on the *same* minute. Two tasks 15 minutes apart still clash in real life, and this check would
miss them. I didn't want to give every task a real duration field, so I added `detect_overlaps()`
as a separate, rougher check that treats each task as a fixed 30-minute block. It stays cheap and
easy to read, and it catches the near-misses the first check drops.

## 3. AI Collaboration

**a. How I used AI**

What helped me most was reading the instructions properly and spending a lot of time planning
and talking to Claude, so my prompt and handoff file could drive the project correctly and I
wouldn't have to spend much time debugging afterward. Planning stage by stage up front helped me
understand exactly what I wanted at each step, instead of going piece by piece and having to
backtrack to fix earlier decisions that didn't fit later ones. The prompts that worked best were
the ones where I locked a decision, like the time model, before asking for any code.

**b. Judgment and verification**

During planning I looked at using a full `datetime` object for each task's time. I dropped that
and kept the simpler `date` + `"HH:MM"` string, because I cared more about it being readable than
clever. A plain `"08:00"` is easy to read, easy to store as JSON, and it sorts fine as a tuple.
There was also a build-time override. The handoff told the agent to push to `origin main` and
make the repo public. The agent flagged that the remote and commit identity looked like they
might belong to a different account, so I overrode that step and had it finish everything locally
so I could review before pushing myself. (See the Agent Workflow log in `ai_interactions.md`.) I
checked the build the same way the whole time. I ran `python main.py` and `python -m pytest` and
read the actual output before believing the code was right.

## 4. Testing and Verification

**a. What I tested**

Five behaviors: a task's completion flag flips, adding a task increases the pet's count,
out-of-order tasks come back sorted by time, completing a daily task makes a next-day occurrence,
and same-time tasks raise a conflict while distinct times do not. The whole daily plan leans on
these, so those are the ones I wanted covered.

**b. Confidence**

**Confidence Level: 5/5 ⭐**. The pytest suite passes and the CLI runs clean from start to finish.
With more time I'd add some edge cases: weekly recurrence across a month boundary,
`next_available_slot` when the whole day is full, and a bad `"HH:MM"` input.

## 5. Reflection

**a. What went well**

I'm happy with how cleanly the logic and the UI came apart. Because `pawpal_system.py` was
finished and tested before `app.py` existed, wiring up the Streamlit UI was mostly calling
methods that already worked.

**b. What I would improve**

I'd model task durations properly instead of assuming a flat 30 minutes. That would let conflict
and overlap detection fold into one accurate check. I'd also add editing and removing tasks from
the UI.

**c. Key takeaway**

Working with the agent felt like having a junior developer who can build the features you
planned, as long as the description is clear. What I took from it is that the design is the part
that counts. Once the plan was precise, the implementation was the easy part, and the result was
only as good as the planning I put in.
