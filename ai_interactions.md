# AI Interactions Log

## Agent Workflow (SF7)

**Files modified / created by the agent**

- `pawpal_system.py`: logic layer (classes, algorithms, JSON persistence, formatting)
- `main.py`: CLI demo
- `app.py`: Streamlit UI wired to the logic layer
- `tests/test_pawpal.py` and `tests/__init__.py`: pytest suite
- `diagrams/uml_draft.mmd` and `diagrams/uml_final.mmd`: Mermaid class diagrams
- `README.md`, `reflection.md`, `ai_interactions.md`: documentation
- `requirements.txt` (added `tabulate`) and `.gitignore` (ignored the runtime `pawpal_data.json`)

**Task requested of the agent**

Build PawPal+ end to end from a locked specification: implement the four classes
(`Owner`, `Pet`, `Task`, `Scheduler`), the scheduling algorithms (sort by time/priority,
filter by pet/status, exact-time conflict detection, 30-minute overlap detection, daily/weekly
recurrence, next-available-slot), JSON persistence, a CLI demo, a Streamlit UI, a 5-test pytest
suite, both UML diagrams, and the docs, then commit in a defined sequence.

**What the agent completed**

All of it. The logic layer was built and checked CLI-first: `python main.py` runs the full
feature set and `python -m pytest` reports **5 passed** (real output is pasted in `README.md`).
Work was committed in the specified 8-commit sequence so the history reads as real steps.

**What had to be verified, corrected, or overridden during the run**

- **The project wasn't local at first.** The `README.md` and `reflection.md` named in the brief
  didn't exist in the working directory. The agent stopped instead of making up a summary, and
  the fork was cloned before any work started.
- **Push step overridden (build-time correction).** The spec told the agent to run
  `git push origin main` and make the repo public. The agent flagged that the `origin` remote
  (`husseinhkareem/...`) and the commit author identity didn't clearly match the session account,
  and asked me to confirm first. I overrode the push step and had it finish everything **locally**
  for review, so nothing was pushed. This is the overridden-suggestion example I mention in
  `reflection.md` §3b.
- **`format_schedule` ordering, self-corrected.** An early version would have had
  `format_schedule()` sort tasks by time on its own. The agent noticed that would quietly break
  the priority-sorted view in `main.py` (section 2), so it made the formatter keep whatever order
  the caller passed in.
- **Runtime data file ignored.** `pawpal_data.json` gets rewritten every run, so it went into
  `.gitignore` instead of being committed as churn.
- **No test failures happened.** The pytest suite passed on the first run. No fixes to
  `next_occurrence` or any other method were needed. I'm recording that as-is rather than
  inventing a bug to fill this section.

---

## AI Model / Prompt Comparison (SF11)

**Tool used:** Claude, through Claude Code.

I wrote `next_available_slot` two ways from two prompts, then ran both on the same three
scenarios to see what actually differed.

**Prompt A (vague):** "Write a next_available_slot method for a scheduler."

**Prompt B (detailed):** "Write next_available_slot(day=None, duration_minutes=30,
day_start='08:00', day_end='20:00'); consider only incomplete tasks that day, treat each as a
30-min block, return the first free HH:MM gap that fits, else a clear no-slot message."

**What each produced**

Version A took no arguments. It sorted every task's `due_time`, took the hour of the last one,
and returned that hour plus one. Version B took the full signature
`next_available_slot(day=None, duration_minutes=30, day_start='08:00', day_end='20:00')`. It
filtered to a single day, dropped completed tasks, walked forward from `day_start`, and returned
the first gap of at least `duration_minutes`. If nothing fit, it returned a no-slot message.

**Real results from the three scenarios**

- Scenario 1 had an 08:00 task marked done, tasks at 09:00, 12:00, and 18:00 today, and one at
  10:00 tomorrow. A returned `19:00`. B returned `08:00`. A landed an hour after the last task
  and never noticed the morning was already free once the 08:00 task was done. B skipped the
  completed task, stayed on today, and found the open 08:00 slot.
- Scenario 2 was an empty day. A returned `No tasks scheduled`. B returned `08:00`. A gave text
  instead of a time you can book. B handed back the first slot of the day.
- Scenario 3 packed the day from 08:00 to 19:30 in 30-minute steps. A returned `20:00`. B
  returned `No 30-minute slot available on 2026-07-06 before 20:00`. A pushed one hour past the
  last task and offered the end of the working day. B saw the day was full and said so.

**Useful output from each**

A is short and easy to read, and for a day with one task late in the afternoon it gives a slot
that looks reasonable. B gave the answer I actually wanted every time. It stayed inside the
working window and skipped tasks that were already done. It also wouldn't offer a gap smaller
than `duration_minutes`.

**Problems with each**

A missed a lot because the prompt didn't pin anything down. It has no `day_start` or `day_end`,
so in Scenario 3 it offered `20:00`, which is the end of the day and past any real opening. It
never filters by day, so a task tomorrow can still change the answer. It ignores the `completed`
flag, so a finished task still blocks time. It only looks after the last task, so it skips
earlier gaps like the free 08:00 in Scenario 1. It also ignores `duration_minutes`, so it can't
tell whether a gap is big enough. B is longer and leans on two helpers that convert `"HH:MM"` to
minutes and back. Its behavior depends on `day_start` and `day_end` being set sensibly, so
there's more to read and more to test.

**Which I'd keep and why**

I'd keep Version B, and it's the one in `pawpal_system.py`. Across the three runs, A gave a wrong
or unusable answer each time (`19:00` instead of `08:00`, a text string instead of a time, and
`20:00` on a full day), while B matched what a planner should say. The comparison also showed me
why prompt B's detail mattered. It spelled out the signature and the working window, so the model
didn't have to guess. Prompt A left those open, and the guesses it made were wrong.
