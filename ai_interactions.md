# AI Interactions Log

## Agent Workflow (SF7)

**Files modified / created by the agent**

- `pawpal_system.py` — logic layer (classes, algorithms, JSON persistence, formatting)
- `main.py` — CLI demo
- `app.py` — Streamlit UI wired to the logic layer
- `tests/test_pawpal.py` and `tests/__init__.py` — pytest suite
- `diagrams/uml_draft.mmd` and `diagrams/uml_final.mmd` — Mermaid class diagrams
- `README.md`, `reflection.md`, `ai_interactions.md` — documentation
- `requirements.txt` (added `tabulate`) and `.gitignore` (ignored the runtime `pawpal_data.json`)

**Task requested of the agent**

Build PawPal+ end-to-end from a locked specification: implement the four classes
(`Owner`, `Pet`, `Task`, `Scheduler`), the scheduling algorithms (sort by time/priority,
filter by pet/status, exact-time conflict detection, 30-minute overlap detection, daily/weekly
recurrence, next-available-slot), JSON persistence, a CLI demo, a Streamlit UI, a 5-test pytest
suite, both UML diagrams, and the docs — committing in a defined sequence.

**What the agent completed**

All of the above. The logic layer was built and verified CLI-first: `python main.py` runs the
full feature set and `python -m pytest` reports **5 passed** (real output pasted in `README.md`).
Work was committed in the specified 8-commit sequence for a meaningful history.

**What had to be verified, corrected, or overridden during the run**

- **The project wasn't local at first.** The `README.md`/`reflection.md` referenced in the
  brief didn't exist in the working directory; the agent stopped instead of fabricating a
  summary, and the fork was cloned before any work began.
- **Push step overridden (build-time correction).** The spec instructed the agent to
  `git push origin main` and make the repo public. The agent flagged that the `origin` remote
  (`husseinhkareem/...`) and the commit author identity didn't obviously match the session
  account, and recommended confirming first. Ali overrode the spec's push step and chose to
  finish everything **locally** for review — so nothing was pushed. This is the "AI suggestion
  overridden" example referenced in `reflection.md` §3b.
- **`format_schedule` ordering, self-corrected.** An early approach would have had
  `format_schedule()` sort tasks by time internally. The agent caught that this would silently
  destroy the priority-sorted view in `main.py` (section 2), and instead made the formatter
  preserve the caller's ordering.
- **Runtime data file ignored.** `pawpal_data.json` is generated on every run, so it was added
  to `.gitignore` rather than committed as noisy churn.
- **No test failures occurred.** The pytest suite passed on its first execution; no bug fixes
  to `next_occurrence` or any other method were needed. (Recorded honestly — nothing was
  invented to fill this section.)
