"""PawPal+ Streamlit UI, wired to the pawpal_system logic layer with persistence."""

from datetime import date

import streamlit as st

from pawpal_system import (
    Owner,
    Pet,
    Task,
    Scheduler,
    format_schedule,
    save_data,
    load_data,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A pet-care planner: add pets, schedule tasks, and see today's prioritized plan.")

# --- State: load once from disk, never re-instantiate on rerun ---
if "owner" not in st.session_state:
    st.session_state.owner = load_data() or Owner("Ali", [])

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

PRIORITY_OPTIONS = {"high (1)": 1, "medium (2)": 2, "low (3)": 3}

# --- Add a pet ---
st.subheader("1. Add a pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Buddy")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if pet_name and owner.get_pet(pet_name) is None:
            owner.add_pet(Pet(pet_name, species))
            save_data(owner)
            st.success(f"Added {pet_name} the {species}.")
        elif owner.get_pet(pet_name) is not None:
            st.warning(f"{pet_name} already exists.")
        else:
            st.warning("Please enter a pet name.")

# --- Add a task ---
st.subheader("2. Schedule a task")
if owner.list_pets():
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.list_pets()])
        description = st.text_input("Task description", value="Morning walk")
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due date", value=date.today())
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        with col2:
            due_time = st.text_input("Due time (HH:MM)", value="08:00")
            priority_label = st.selectbox("Priority", list(PRIORITY_OPTIONS.keys()))
        if st.form_submit_button("Add task"):
            pet = owner.get_pet(pet_choice)
            pet.add_task(
                Task(description, pet_choice, due_date, due_time,
                     frequency, priority=PRIORITY_OPTIONS[priority_label])
            )
            save_data(owner)
            st.success(f"Scheduled '{description}' for {pet_choice} at {due_time}.")
else:
    st.info("Add a pet first to schedule tasks.")

# --- Today's schedule ---
st.subheader("3. Today's schedule")
view = st.radio("View", ["By time", "By priority"], horizontal=True)
pet_filter = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.list_pets()])
status_filter = st.selectbox("Filter by status", ["All", "Incomplete", "Complete"])

tasks = scheduler.todays_schedule()
if pet_filter != "All":
    tasks = [t for t in tasks if t.pet_name == pet_filter]
if status_filter == "Incomplete":
    tasks = [t for t in tasks if not t.completed]
elif status_filter == "Complete":
    tasks = [t for t in tasks if t.completed]
tasks = scheduler.sort_by_priority(tasks) if view == "By priority" else scheduler.sort_by_time(tasks)

if tasks:
    st.table([
        {"Time": t.due_time, "Pet": t.pet_name, "Task": t.description,
         "Freq": t.frequency, "Priority": t.priority, "Done": "✅" if t.completed else "⬜"}
        for t in tasks
    ])
else:
    st.info("No tasks for today yet.")

# --- Warnings and next slot ---
st.subheader("4. Scheduling warnings")
conflicts = scheduler.detect_conflicts()
overlaps = scheduler.detect_overlaps()
if not conflicts and not overlaps:
    st.success("No conflicts or overlaps detected.")
for warning in conflicts:
    st.warning(warning)
for warning in overlaps:
    st.warning(warning)
st.info(f"Next available 30-min slot today: {scheduler.next_available_slot()}")
