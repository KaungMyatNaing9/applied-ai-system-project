"""
pawpal_system.py
Backend logic layer for PawPal+ — a pet care planning application.
"""

from __future__ import annotations
import datetime
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

# Priority rank used for sorting — higher number = higher urgency.
_PRIORITY_RANK: dict[str, int] = {"low": 1, "medium": 2, "high": 3}

_VALID_PRIORITIES = frozenset(_PRIORITY_RANK)


@dataclass
class Task:
    """Represents a single pet care activity.

    Attributes:
        id:               Unique identifier for this task.
        title:            Short name of the activity (e.g. "Morning Walk").
        duration_minutes: Estimated time the activity takes.
        priority:         Urgency level — "low", "medium", or "high".
        category:         Type of care — e.g. "feeding", "exercise",
                          "grooming", "medical".
        frequency:        How often the task recurs — "once", "daily",
                          or "weekly".
        is_completed:     Whether the task has been done today.
    """

    id: int
    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    category: str           # "feeding" | "exercise" | "grooming" | "medical" | …
    frequency: str = "daily"
    is_completed: bool = False
    time: str | None = None            # Scheduled start time, 'HH:MM' format
    due_date: datetime.date | None = None  # Date this occurrence is due

    # ------------------------------------------------------------------
    # Completion helpers
    # ------------------------------------------------------------------

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to incomplete."""
        self.is_completed = False

    def get_next_occurrence(self, next_id: int) -> Task | None:
        """Return a fresh Task for the next recurrence of this task.

        Args:
            next_id: The id to assign to the new Task instance.

        Returns:
            A new Task due one period later, or None if frequency is "once".
        """
        if self.frequency == "once":
            return None
        delta = (
            datetime.timedelta(days=1)
            if self.frequency == "daily"
            else datetime.timedelta(weeks=1)
        )
        base = self.due_date if self.due_date is not None else datetime.date.today()
        return Task(
            id=next_id,
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            frequency=self.frequency,
            is_completed=False,
            time=self.time,
            due_date=base + delta,
        )

    # ------------------------------------------------------------------
    # Attribute updates
    # ------------------------------------------------------------------

    def update_duration(self, minutes: int) -> None:
        """Update the estimated duration of this task.

        Args:
            minutes: New duration; must be a positive integer.

        Raises:
            ValueError: If *minutes* is not a positive integer.
        """
        if minutes <= 0:
            raise ValueError(f"duration_minutes must be positive, got {minutes}")
        self.duration_minutes = minutes

    def update_priority(self, level: str) -> None:
        """Update the priority level of this task.

        Args:
            level: One of "low", "medium", or "high".

        Raises:
            ValueError: If *level* is not a recognised priority string.
        """
        level = level.lower()
        if level not in _VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority '{level}'. Choose from {sorted(_VALID_PRIORITIES)}."
            )
        self.priority = level

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def get_details(self) -> str:
        """Return a human-readable summary of this task.

        Returns:
            A formatted string describing all task attributes.
        """
        status = "Done" if self.is_completed else "Pending"
        return (
            f"[{self.id}] {self.title} | "
            f"{self.duration_minutes} min | "
            f"Priority: {self.priority} | "
            f"Category: {self.category} | "
            f"Frequency: {self.frequency} | "
            f"Status: {status}"
        )

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title={self.title!r}, priority={self.priority!r})"


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents a pet and its associated care tasks.

    Attributes:
        id:         Unique identifier for this pet.
        name:       The pet's name.
        species:    Kind of animal — e.g. "dog", "cat", "bird".
        age:        Age in years.
        care_needs: Free-text list of recurring needs (e.g. "insulin shot").
        tasks:      Care tasks associated with this pet.
    """

    id: int
    name: str
    species: str
    age: int
    care_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet.

        Duplicate task ids are silently ignored.

        Args:
            task: The Task to add.
        """
        if any(t.id == task.id for t in self.tasks):
            return
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove a task from this pet by its id.

        Args:
            task_id: The id of the Task to remove.

        Raises:
            ValueError: If no task with *task_id* is found.
        """
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                self.tasks.pop(i)
                return
        raise ValueError(f"No task with id {task_id} found for pet '{self.name}'.")

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not yet been completed.

        Returns:
            List of incomplete Task objects.
        """
        return [t for t in self.tasks if not t.is_completed]

    def complete_task(self, task_id: int, next_task_id: int) -> Task | None:
        """Mark a task complete and automatically queue its next occurrence.

        For recurring tasks ("daily" or "weekly") a new Task is appended to
        this pet's task list so the care schedule stays up to date.

        Args:
            task_id:      The id of the Task to complete.
            next_task_id: The id to assign to the newly created recurrence.

        Returns:
            The next-occurrence Task if one was created, otherwise None.

        Raises:
            ValueError: If no task with *task_id* exists on this pet.
        """
        for task in self.tasks:
            if task.id == task_id:
                task.mark_complete()
                next_task = task.get_next_occurrence(next_task_id)
                if next_task is not None:
                    self.tasks.append(next_task)
                return next_task
        raise ValueError(f"No task with id {task_id} found for pet '{self.name}'.")

    # ------------------------------------------------------------------
    # Care-needs management
    # ------------------------------------------------------------------

    def get_care_needs(self) -> List[str]:
        """Return the list of care needs for this pet.

        Returns:
            A copy of the care_needs list.
        """
        return list(self.care_needs)

    def update_care_needs(self, needs: List[str]) -> None:
        """Replace the current care needs list.

        Args:
            needs: New list of care need strings.
        """
        self.care_needs = list(needs)

    def __repr__(self) -> str:
        return f"Pet(id={self.id}, name={self.name!r}, species={self.species!r})"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Represents the pet owner and their scheduling constraints.

    Attributes:
        name:                 The owner's name.
        daily_available_time: Total minutes available for pet care today.
        preferences:          Free-text scheduling preferences, e.g.
                              ["morning tasks first", "no tasks after 8 pm"].
        pets:                 Pets registered to this owner.
    """

    def __init__(
        self,
        name: str,
        daily_available_time: int,
        preferences: List[str] | None = None,
    ) -> None:
        self.name: str = name
        self.daily_available_time: int = daily_available_time
        self.preferences: List[str] = preferences if preferences is not None else []
        self.pets: List[Pet] = []

    # ------------------------------------------------------------------
    # Pet management
    # ------------------------------------------------------------------

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster.

        Duplicate pet ids are silently ignored.

        Args:
            pet: The Pet to add.
        """
        if any(p.id == pet.id for p in self.pets):
            return
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet by its id.

        Args:
            pet_id: The id of the Pet to remove.

        Raises:
            ValueError: If no pet with *pet_id* exists.
        """
        for i, p in enumerate(self.pets):
            if p.id == pet_id:
                self.pets.pop(i)
                return
        raise ValueError(f"No pet with id {pet_id} found for owner '{self.name}'.")

    # ------------------------------------------------------------------
    # Task aggregation
    # ------------------------------------------------------------------

    def get_all_tasks(self) -> List[Task]:
        """Aggregate and return every task across all pets.

        Returns:
            A flat list of all Task objects owned by this owner's pets.
        """
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks across every pet.

        Returns:
            A flat list of pending Task objects.
        """
        return [t for t in self.get_all_tasks() if not t.is_completed]

    # ------------------------------------------------------------------
    # Time & preferences
    # ------------------------------------------------------------------

    def get_available_time(self) -> int:
        """Return the owner's total daily available time in minutes.

        Returns:
            Available minutes as an integer.
        """
        return self.daily_available_time

    def update_preferences(self, preferences: List[str]) -> None:
        """Replace the owner's scheduling preferences.

        Args:
            preferences: New list of preference strings.
        """
        self.preferences = list(preferences)

    def __repr__(self) -> str:
        return (
            f"Owner(name={self.name!r}, "
            f"daily_available_time={self.daily_available_time}, "
            f"pets={[p.name for p in self.pets]})"
        )


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Generates and explains a daily pet care plan for an owner.

    The scheduling algorithm:
      1. Collect all pending tasks from every pet via the Owner.
      2. Sort by priority (high → medium → low), then by duration
         (shortest first within the same priority tier — quick wins).
      3. Greedily select tasks until the time budget is exhausted.
      4. Store the result in ``scheduled_tasks``.

    Attributes:
        owner:           The Owner being scheduled for.
        scheduled_tasks: The ordered list produced by the last call to
                         ``generate_daily_plan``.
    """

    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner
        self.scheduled_tasks: List[Task] = []
        self.conflict_warnings: List[str] = []  # Populated by generate_daily_plan()

    # ------------------------------------------------------------------
    # Core scheduling
    # ------------------------------------------------------------------

    def generate_daily_plan(self) -> List[Task]:
        """Build an ordered list of tasks that fits within the owner's
        available time, ranked by priority then shortest-first.

        After selecting tasks, conflict detection runs automatically and
        any warnings are stored in ``self.conflict_warnings``.

        Side-effects:
            Populates ``self.scheduled_tasks`` with the chosen tasks.
            Populates ``self.conflict_warnings`` with any detected issues.

        Returns:
            The ordered list of scheduled Task objects.
        """
        self.scheduled_tasks = []
        self.conflict_warnings = []

        pending = self.owner.get_pending_tasks()
        sorted_tasks = self.organize_by_priority(pending)
        self.scheduled_tasks = self.filter_by_duration(
            sorted_tasks, self.owner.get_available_time()
        )
        self.conflict_warnings = self.detect_conflicts()
        return self.scheduled_tasks

    def organize_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks so that higher-priority items appear first.

        Within the same priority tier tasks are ordered shortest-first
        to maximise the number of tasks completed.

        Args:
            tasks: Unsorted list of Task objects.

        Returns:
            A new list sorted by (descending priority, ascending duration).
        """
        return sorted(
            tasks,
            key=lambda t: (-_PRIORITY_RANK.get(t.priority, 0), t.duration_minutes),
        )

    def filter_by_duration(
        self, tasks: List[Task], available_time: int
    ) -> List[Task]:
        """Greedily select tasks that fit within the available time budget.

        Tasks are evaluated in the order supplied. Each task is included
        if it fits in the remaining budget.

        Args:
            tasks:          Candidate tasks, already sorted by priority.
            available_time: Total minutes the owner has available today.

        Returns:
            A subset of *tasks* that fits within *available_time*.
        """
        selected: List[Task] = []
        remaining = available_time
        for task in tasks:
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
        return selected

    def check_conflicts(self, task: Task) -> bool:
        """Check whether a task's title already appears in the current plan.

        Args:
            task: The Task being considered for addition.

        Returns:
            True if a task with the same title is already scheduled,
            False otherwise.
        """
        return any(t.title == task.title for t in self.scheduled_tasks)

    # ------------------------------------------------------------------
    # Sorting by time
    # ------------------------------------------------------------------

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by their scheduled start time ('HH:MM').

        Tasks without a ``time`` value sort to the end of the list.

        Args:
            tasks: The Task objects to sort.

        Returns:
            A new list ordered by ascending start time.
        """
        return sorted(tasks, key=lambda t: t.time if t.time is not None else "99:99")

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_by_status(self, completed: bool) -> List[Task]:
        """Return all tasks across every pet filtered by completion status.

        Args:
            completed: Pass True to retrieve completed tasks, False for pending.

        Returns:
            A flat list of matching Task objects.
        """
        return [t for t in self.owner.get_all_tasks() if t.is_completed == completed]

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to a specific pet (case-insensitive).

        Args:
            pet_name: The name of the pet to look up.

        Returns:
            A list of that pet's Task objects, or an empty list if not found.
        """
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return list(pet.tasks)
        return []

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    @staticmethod
    def _to_datetime(time_str: str) -> datetime.datetime:
        """Parse an 'HH:MM' string into a comparable datetime object."""
        h, m = map(int, time_str.split(":"))
        return datetime.datetime(2000, 1, 1, h, m)

    def _task_pet_map(self) -> dict[int, str]:
        """Return a mapping of task id → pet name for every registered task."""
        return {
            task.id: pet.name
            for pet in self.owner.pets
            for task in pet.tasks
        }

    def detect_conflicts(self) -> List[str]:
        """Analyse the scheduled plan and return human-readable conflict warnings.

        Checks are run against ``self.scheduled_tasks`` (populated by
        ``generate_daily_plan``).  No exceptions are raised; problems are
        reported as plain strings so callers can decide how to surface them.

        Conflict types detected:

        * **Budget overflow** — the total scheduled time exceeds the owner's
          daily limit (can happen if tasks are added to ``scheduled_tasks``
          directly, bypassing ``filter_by_duration``).
        * **Unschedulable task** — a pending task is longer than the entire
          daily budget and can never be selected.
        * **Time overlap** — two scheduled tasks with explicit ``time`` values
          have windows that intersect, meaning they cannot both run as planned.
          The warning names both tasks *and* their respective pets so same-pet
          and cross-pet conflicts are equally clear.

        Returns:
            A list of warning strings.  An empty list means no conflicts found.
        """
        warnings: List[str] = []
        budget = self.owner.get_available_time()
        pet_of = self._task_pet_map()

        # 1. Budget overflow in the current plan
        used = sum(t.duration_minutes for t in self.scheduled_tasks)
        if used > budget:
            warnings.append(
                f"WARNING — Budget overflow: {used} min scheduled "
                f"but only {budget} min available."
            )

        # 2. Pending tasks that can never fit inside the budget
        for task in self.owner.get_pending_tasks():
            if task.duration_minutes > budget:
                pet_name = pet_of.get(task.id, "unknown pet")
                warnings.append(
                    f"WARNING — Unschedulable task: '{task.title}' "
                    f"({pet_name}, {task.duration_minutes} min) exceeds "
                    f"the daily budget of {budget} min and can never be scheduled."
                )

        # 3. Time-window overlaps between timed tasks in the scheduled plan
        timed = [
            (t, self._to_datetime(t.time))
            for t in self.scheduled_tasks
            if t.time is not None
        ]
        for i, (task_a, start_a) in enumerate(timed):
            end_a = start_a + datetime.timedelta(minutes=task_a.duration_minutes)
            for task_b, start_b in timed[i + 1:]:
                end_b = start_b + datetime.timedelta(minutes=task_b.duration_minutes)
                if start_a < end_b and start_b < end_a:
                    pet_a = pet_of.get(task_a.id, "unknown pet")
                    pet_b = pet_of.get(task_b.id, "unknown pet")
                    same = pet_a == pet_b
                    scope = f"same pet: {pet_a}" if same else f"cross-pet: {pet_a} / {pet_b}"
                    warnings.append(
                        f"WARNING — Time overlap ({scope}): "
                        f"'{task_a.title}' starts {task_a.time} "
                        f"and runs {task_a.duration_minutes} min, "
                        f"overlapping '{task_b.title}' which starts {task_b.time} "
                        f"and runs {task_b.duration_minutes} min."
                    )

        return warnings

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------

    def explain_plan(self) -> str:
        """Produce a plain-language explanation of the current daily plan.

        Describes the total time budget, how many tasks were selected,
        and for each task explains why it was included and where it
        falls in the order.

        Returns:
            A multi-line string summarising the scheduling rationale.
            Returns a short notice if no plan has been generated yet.
        """
        if not self.scheduled_tasks:
            return "No plan generated yet. Call generate_daily_plan() first."

        total_budget = self.owner.get_available_time()
        used = sum(t.duration_minutes for t in self.scheduled_tasks)
        remaining = total_budget - used

        lines: List[str] = [
            f"Daily Plan for {self.owner.name}",
            f"Time budget: {total_budget} min | "
            f"Scheduled: {used} min | "
            f"Remaining: {remaining} min",
            f"Tasks selected: {len(self.scheduled_tasks)}",
            "-" * 50,
        ]

        for rank, task in enumerate(self.scheduled_tasks, start=1):
            reason = (
                f"Priority '{task.priority}' — "
                + (
                    "scheduled first as the most urgent."
                    if task.priority == "high"
                    else "scheduled after high-priority tasks."
                    if task.priority == "medium"
                    else "scheduled last as a lower-urgency activity."
                )
            )
            lines.append(
                f"{rank}. {task.title} ({task.duration_minutes} min) — {reason}"
            )

        lines.append("-" * 50)
        lines.append(
            "Tasks not scheduled: either already completed or exceeded time budget."
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def get_remaining_time(self) -> int:
        """Return how many minutes remain after the current scheduled plan.

        Returns:
            Unallocated minutes from the owner's daily time budget.
        """
        used = sum(t.duration_minutes for t in self.scheduled_tasks)
        return self.owner.get_available_time() - used

    def reset_plan(self) -> None:
        """Clear the current scheduled plan so a new one can be generated."""
        self.scheduled_tasks = []

    def __repr__(self) -> str:
        return (
            f"Scheduler(owner={self.owner.name!r}, "
            f"scheduled_tasks={len(self.scheduled_tasks)})"
        )


# ---------------------------------------------------------------------------
# Sample data helper
# ---------------------------------------------------------------------------

def load_sample_data() -> Scheduler:
    """Build a Scheduler pre-loaded with a sample owner and pets.

    Returns:
        A ready-to-use Scheduler instance with sample data.
    """
    owner = Owner(name="Jordan", daily_available_time=90)

    luna = Pet(id=1, name="Luna", species="dog", age=4,
               care_needs=["daily exercise", "dental chew"])
    luna.add_task(Task(id=1, title="Morning Walk",
                       duration_minutes=30, priority="high",
                       category="exercise", frequency="daily"))
    luna.add_task(Task(id=2, title="Dinner",
                       duration_minutes=10, priority="high",
                       category="feeding", frequency="daily"))
    luna.add_task(Task(id=3, title="Dental Chew",
                       duration_minutes=5, priority="medium",
                       category="grooming", frequency="daily"))

    milo = Pet(id=2, name="Milo", species="cat", age=2)
    milo.add_task(Task(id=4, title="Brush Fur",
                       duration_minutes=10, priority="medium",
                       category="grooming", frequency="weekly"))
    milo.add_task(Task(id=5, title="Playtime",
                       duration_minutes=20, priority="low",
                       category="exercise", frequency="daily"))

    owner.add_pet(luna)
    owner.add_pet(milo)

    return Scheduler(owner)
