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
