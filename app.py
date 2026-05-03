import re
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session-state initialisation
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", daily_available_time=90)

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

if "feedback" not in st.session_state:
    st.session_state.feedback = None   # ("success"|"warning"|"error", message) | None

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🐾 PawPal+")
st.caption("A daily pet care planner for busy owners.")
st.divider()

# ---------------------------------------------------------------------------
# One-shot feedback banner (cleared after display)
# ---------------------------------------------------------------------------

if st.session_state.feedback:
    level, msg = st.session_state.feedback
    {"success": st.success, "warning": st.warning, "error": st.error}[level](msg)
    st.session_state.feedback = None

# ---------------------------------------------------------------------------
# Section 1 — Owner settings
# ---------------------------------------------------------------------------

st.subheader("Owner")

with st.form("owner_form"):
    col_name, col_time = st.columns(2)
    with col_name:
        new_name = st.text_input("Your name", value=owner.name)
    with col_time:
        new_time = st.number_input(
            "Daily time available (minutes)",
            min_value=10, max_value=480,
            value=owner.daily_available_time, step=5,
        )
    save_owner = st.form_submit_button("Save owner settings")

if save_owner:
    st.session_state.owner.name = new_name
    st.session_state.owner.daily_available_time = new_time
    owner = st.session_state.owner
    st.session_state.feedback = ("success", f"Owner updated: {new_name}, {new_time} min/day.")
    st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Add a Pet
# ---------------------------------------------------------------------------

st.subheader("Add a Pet")

with st.form("add_pet_form", clear_on_submit=True):
    col_pet, col_species, col_age = st.columns(3)
    with col_pet:
        pet_name = st.text_input("Pet name", value="Bella")
    with col_species:
        species = st.selectbox("Species", ["dog", "cat", "bird", "other"])
    with col_age:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    add_pet_btn = st.form_submit_button("Add pet")

if add_pet_btn:
    new_pet = Pet(
        id=st.session_state.next_pet_id,
        name=pet_name,
        species=species,
        age=int(age),
    )
    st.session_state.owner.add_pet(new_pet)
    st.session_state.next_pet_id += 1
    st.session_state.feedback = ("success", f"Added {pet_name} the {species}.")
    st.rerun()

if owner.pets:
    st.caption("Current pets:")
    for pet in owner.pets:
        st.write(f"- **{pet.name}** ({pet.species.capitalize()}, age {pet.age})")
else:
    st.info("No pets added yet.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Add a Task
#
# Now includes optional scheduled time ('HH:MM') and frequency so the
# backend's sorting and recurrence logic can be fully exercised.
# ---------------------------------------------------------------------------

st.subheader("Add a Task")

if not owner.pets:
    st.info("Add at least one pet above before adding tasks.")
else:
    pet_options: dict[str, Pet] = {p.name: p for p in owner.pets}

    with st.form("add_task_form", clear_on_submit=True):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            selected_pet_name = st.selectbox("Assign to pet", list(pet_options.keys()))
        with col_t2:
            task_title = st.text_input("Task title", value="Morning walk")

        col_t3, col_t4, col_t5 = st.columns(3)
        with col_t3:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col_t4:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col_t5:
            category = st.selectbox(
                "Category",
                ["exercise", "feeding", "grooming", "medical", "hygiene", "other"],
            )

        col_t6, col_t7 = st.columns(2)
        with col_t6:
            task_time = st.text_input(
                "Scheduled time (optional)",
                placeholder="HH:MM",
                help="Enter the planned start time in 24-hour format, e.g. 08:30",
            )
        with col_t7:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"], index=0)

        add_task_btn = st.form_submit_button("Add task")

    if add_task_btn:
        # Validate the optional time field before creating the task.
        parsed_time: str | None = None
        time_error: str | None = None
        if task_time.strip():
            if re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", task_time.strip()):
                parsed_time = task_time.strip()
            else:
                time_error = f"'{task_time}' is not a valid time. Use HH:MM (e.g. 08:30)."

        if time_error:
            st.session_state.feedback = ("error", time_error)
            st.rerun()
        else:
            new_task = Task(
                id=st.session_state.next_task_id,
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                frequency=frequency,
                time=parsed_time,
            )
            pet_options[selected_pet_name].add_task(new_task)
            st.session_state.next_task_id += 1
            time_label = f" @ {parsed_time}" if parsed_time else ""
            st.session_state.feedback = (
                "success",
                f"Added '{task_title}'{time_label} to {selected_pet_name} ({frequency}).",
            )
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Your Pets & Tasks
#
# Tasks are displayed sorted by scheduled time (via Scheduler.sort_by_time)
# so the list is immediately chronological.
# ---------------------------------------------------------------------------

st.subheader("Your Pets & Tasks")

if not owner.pets:
    st.info("No pets added yet.")
else:
    _scratch_scheduler = Scheduler(owner)   # used only for sort_by_time

    for pet in owner.pets:
        task_count = len(pet.tasks)
        done_count = sum(1 for t in pet.tasks if t.is_completed)
        label = (
            f"{pet.name} ({pet.species.capitalize()}, age {pet.age})"
            f" — {task_count} task(s), {done_count} done"
        )
        with st.expander(label, expanded=True):
            if not pet.tasks:
                st.caption("No tasks yet.")
            else:
                sorted_tasks = _scratch_scheduler.sort_by_time(pet.tasks)
                rows = [
                    {
                        "Time": t.time if t.time else "—",
                        "Task": t.title,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority.capitalize(),
                        "Category": t.category.capitalize(),
                        "Frequency": t.frequency,
                        "Done": "✓" if t.is_completed else "○",
                    }
                    for t in sorted_tasks
                ]
                st.table(rows)

st.divider()

# ---------------------------------------------------------------------------
# Section 5 — Filter & Explore Tasks
#
# Lets the owner quickly query tasks by pet or completion status using
# Scheduler.filter_by_pet() and Scheduler.filter_by_status().
# ---------------------------------------------------------------------------

st.subheader("Filter & Explore Tasks")

all_tasks = owner.get_all_tasks()

if not all_tasks:
    st.info("Add tasks above to use filtering.")
else:
    _filter_scheduler = Scheduler(owner)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        pet_filter = st.selectbox(
            "Filter by pet",
            ["All pets"] + [p.name for p in owner.pets],
            key="pet_filter",
        )
    with col_f2:
        status_filter = st.radio(
            "Filter by status",
            ["All", "Pending", "Completed"],
            horizontal=True,
            key="status_filter",
        )

    # Fetch the right task pool from the backend.
    if pet_filter == "All pets":
        filtered = all_tasks
    else:
        filtered = _filter_scheduler.filter_by_pet(pet_filter)

    if status_filter == "Pending":
        filtered = [t for t in filtered if not t.is_completed]
    elif status_filter == "Completed":
        filtered = [t for t in filtered if t.is_completed]

    filtered_sorted = _filter_scheduler.sort_by_time(filtered)

    st.caption(f"{len(filtered_sorted)} task(s) match your filter.")

    if not filtered_sorted:
        st.info("No tasks match the selected filters.")
    else:
        # Build a pet-name lookup so the table can show which pet owns each task.
        task_pet_map: dict[int, str] = {
            t.id: p.name for p in owner.pets for t in p.tasks
        }
        filter_rows = [
            {
                "Pet": task_pet_map.get(t.id, "—"),
                "Time": t.time if t.time else "—",
                "Task": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority.capitalize(),
                "Category": t.category.capitalize(),
                "Status": "✓ Done" if t.is_completed else "○ Pending",
            }
            for t in filtered_sorted
        ]
        st.table(filter_rows)

st.divider()

# ---------------------------------------------------------------------------
# Section 6 — Generate Today's Schedule
#
# Calls Scheduler.generate_daily_plan(), which automatically runs
# detect_conflicts() and stores results in scheduler.conflict_warnings.
# The schedule is displayed sorted by time; each conflict warning is shown
# as a dedicated st.warning() block with pet and task context.
# ---------------------------------------------------------------------------

st.subheader("Generate Today's Schedule")

if not all_tasks:
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule", type="primary"):
        scheduler = Scheduler(owner)
        plan = scheduler.generate_daily_plan()   # also populates conflict_warnings

        if not plan:
            st.warning(
                "No tasks could be scheduled. "
                "Try increasing your available time or reducing task durations."
            )
        else:
            used      = sum(t.duration_minutes for t in plan)
            remaining = scheduler.get_remaining_time()

            # --- Summary banner ---
            st.success(
                f"Plan ready — {len(plan)} task(s) scheduled, "
                f"{used} min used, {remaining} min free."
            )

            # --- Schedule table sorted chronologically by start time ---
            task_pet_map = {t.id: p.name for p in owner.pets for t in p.tasks}
            time_sorted_plan = scheduler.sort_by_time(plan)

            schedule_rows = [
                {
                    "#": i,
                    "Pet": task_pet_map.get(t.id, "—"),
                    "Time": t.time if t.time else "—",
                    "Task": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.capitalize(),
                    "Category": t.category.capitalize(),
                }
                for i, t in enumerate(time_sorted_plan, start=1)
            ]
            st.table(schedule_rows)

            # --- Skipped tasks ---
            scheduled_ids = {t.id for t in plan}
            skipped = [
                t for t in owner.get_all_tasks()
                if t.id not in scheduled_ids
            ]
            if skipped:
                with st.expander(f"Skipped tasks ({len(skipped)})"):
                    for t in skipped:
                        pet_name = task_pet_map.get(t.id, "?")
                        reason = "already completed" if t.is_completed else "exceeded time budget"
                        st.write(
                            f"- **{t.title}** ({pet_name}, {t.duration_minutes} min)"
                            f" — {reason}"
                        )

            # --- Conflict warnings ---
            st.markdown("#### Conflict Check")
            if not scheduler.conflict_warnings:
                st.success("No scheduling conflicts detected — your plan looks clean!")
            else:
                for warning in scheduler.conflict_warnings:
                    # Strip the leading "WARNING — " prefix for a cleaner UI label.
                    display_msg = warning.removeprefix("WARNING — ")
                    st.warning(f"⚠️ {display_msg}")

            # --- Scheduling rationale ---
            with st.expander("Why this order?"):
                st.text(scheduler.explain_plan())
