import datetime
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Fixtures — reusable building blocks
# ---------------------------------------------------------------------------

@pytest.fixture
def owner():
    return Owner(name="Alex", daily_available_time=90)


@pytest.fixture
def pet():
    return Pet(id=1, name="Bella", species="dog", age=3)


@pytest.fixture
def scheduler(owner):
    return Scheduler(owner)


# ---------------------------------------------------------------------------
# Existing tests (unchanged)
# ---------------------------------------------------------------------------

def test_mark_complete_sets_is_completed_to_true():
    task = Task(id=1, title="Morning Walk", duration_minutes=30,
                priority="high", category="exercise")

    task.mark_complete()

    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(id=1, name="Bella", species="dog", age=3)
    task = Task(id=1, title="Breakfast", duration_minutes=10,
                priority="high", category="feeding")

    pet.add_task(task)

    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order(owner, scheduler):
    """Tasks added in random time order must come back sorted 07:00 → 18:00."""
    pet = Pet(id=1, name="Bella", species="dog", age=3)
    pet.add_task(Task(id=1, title="Evening Walk",   duration_minutes=30,
                      priority="medium", category="exercise", time="18:00"))
    pet.add_task(Task(id=2, title="Breakfast",      duration_minutes=10,
                      priority="high",   category="feeding",  time="07:30"))
    pet.add_task(Task(id=3, title="Midday Check",   duration_minutes=5,
                      priority="low",    category="grooming",  time="12:00"))
    pet.add_task(Task(id=4, title="Morning Meds",   duration_minutes=5,
                      priority="high",   category="medical",   time="07:00"))
    owner.add_pet(pet)

    sorted_tasks = scheduler.sort_by_time(pet.tasks)
    times = [t.time for t in sorted_tasks]

    assert times == ["07:00", "07:30", "12:00", "18:00"]


def test_sort_by_time_tasks_without_time_sort_last(owner, scheduler):
    """Tasks that have no time value must appear after all timed tasks."""
    pet = Pet(id=1, name="Bella", species="dog", age=3)
    pet.add_task(Task(id=1, title="Dental Chew", duration_minutes=5,
                      priority="medium", category="grooming", time=None))
    pet.add_task(Task(id=2, title="Feeding",     duration_minutes=5,
                      priority="high",   category="feeding",  time="08:00"))
    owner.add_pet(pet)

    sorted_tasks = scheduler.sort_by_time(pet.tasks)

    assert sorted_tasks[0].time == "08:00"
    assert sorted_tasks[-1].time is None


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_complete_daily_task_creates_next_day_occurrence(pet):
    """Completing a daily task must produce a new task due tomorrow."""
    today = datetime.date.today()
    task = Task(id=1, title="Breakfast", duration_minutes=10,
                priority="high", category="feeding",
                frequency="daily", due_date=today)
    pet.add_task(task)

    next_task = pet.complete_task(task_id=1, next_task_id=99)

    assert next_task is not None
    assert next_task.due_date == today + datetime.timedelta(days=1)
    assert next_task.is_completed is False
    assert next_task.title == task.title


def test_complete_weekly_task_creates_next_week_occurrence(pet):
    """Completing a weekly task must produce a new task due in 7 days."""
    today = datetime.date.today()
    task = Task(id=2, title="Brush Fur", duration_minutes=10,
                priority="medium", category="grooming",
                frequency="weekly", due_date=today)
    pet.add_task(task)

    next_task = pet.complete_task(task_id=2, next_task_id=98)

    assert next_task is not None
    assert next_task.due_date == today + datetime.timedelta(weeks=1)


def test_complete_once_task_produces_no_recurrence(pet):
    """A one-off task must not generate a follow-up occurrence."""
    task = Task(id=3, title="Vet Visit", duration_minutes=60,
                priority="high", category="medical",
                frequency="once")
    pet.add_task(task)

    next_task = pet.complete_task(task_id=3, next_task_id=97)

    assert next_task is None


def test_recurring_task_appended_to_pet_task_list(pet):
    """After completion, the pet's task list must contain the new occurrence."""
    today = datetime.date.today()
    task = Task(id=1, title="Evening Walk", duration_minutes=30,
                priority="medium", category="exercise",
                frequency="daily", due_date=today)
    pet.add_task(task)
    original_count = len(pet.tasks)

    pet.complete_task(task_id=1, next_task_id=50)

    assert len(pet.tasks) == original_count + 1


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_tasks(owner):
    """Two tasks sharing the same start time must produce a time-overlap warning."""
    pet = Pet(id=1, name="Bella", species="dog", age=3)
    pet.add_task(Task(id=1, title="Morning Walk", duration_minutes=30,
                      priority="high", category="exercise", time="07:00"))
    pet.add_task(Task(id=2, title="Breakfast",    duration_minutes=10,
                      priority="high", category="feeding",  time="07:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_daily_plan()

    overlap_warnings = [w for w in scheduler.conflict_warnings if "overlap" in w.lower()]
    assert len(overlap_warnings) >= 1


def test_detect_conflicts_cross_pet_overlap(owner):
    """A time-window overlap between two different pets must be flagged as cross-pet."""
    bella  = Pet(id=1, name="Bella",  species="dog", age=3)
    oliver = Pet(id=2, name="Oliver", species="cat", age=5)
    bella.add_task(Task(id=1, title="Morning Walk", duration_minutes=30,
                        priority="high", category="exercise", time="07:00"))
    oliver.add_task(Task(id=2, title="Feeding",     duration_minutes=10,
                         priority="high", category="feeding",  time="07:00"))
    owner.add_pet(bella)
    owner.add_pet(oliver)

    scheduler = Scheduler(owner)
    scheduler.generate_daily_plan()

    cross_pet_warnings = [w for w in scheduler.conflict_warnings if "cross-pet" in w.lower()]
    assert len(cross_pet_warnings) >= 1


def test_detect_conflicts_flags_unschedulable_task(owner):
    """A task longer than the daily budget must be flagged as unschedulable."""
    pet = Pet(id=1, name="Bella", species="dog", age=3)
    # owner budget is 90 min; this task needs 120
    pet.add_task(Task(id=1, title="Marathon Vet", duration_minutes=120,
                      priority="low", category="medical"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_daily_plan()

    unschedulable = [w for w in scheduler.conflict_warnings if "unschedulable" in w.lower()]
    assert len(unschedulable) == 1
    assert "Marathon Vet" in unschedulable[0]


def test_no_conflicts_when_tasks_do_not_overlap(owner):
    """Non-overlapping timed tasks must produce zero conflict warnings."""
    pet = Pet(id=1, name="Bella", species="dog", age=3)
    pet.add_task(Task(id=1, title="Morning Walk", duration_minutes=30,
                      priority="high", category="exercise", time="07:00"))
    pet.add_task(Task(id=2, title="Dental Chew",  duration_minutes=5,
                      priority="medium", category="grooming", time="09:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_daily_plan()

    assert scheduler.conflict_warnings == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_does_not_break_schedule(owner):
    """A pet registered with zero tasks must not raise and must yield an empty plan."""
    empty_pet = Pet(id=1, name="Ghost", species="cat", age=2)
    owner.add_pet(empty_pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()

    assert plan == []
    assert scheduler.conflict_warnings == []


def test_empty_owner_produces_empty_plan(owner):
    """An owner with no pets must return an empty plan without errors."""
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()

    assert plan == []


def test_all_tasks_completed_produces_empty_plan(owner):
    """When every task is already marked complete, the plan must be empty."""
    pet = Pet(id=1, name="Bella", species="dog", age=3)
    task = Task(id=1, title="Morning Walk", duration_minutes=30,
                priority="high", category="exercise")
    task.mark_complete()
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()

    assert plan == []


def test_duplicate_task_id_is_silently_ignored(pet):
    """Adding a task with an id that already exists must not create a duplicate."""
    task_a = Task(id=1, title="Walk",      duration_minutes=30,
                  priority="high", category="exercise")
    task_b = Task(id=1, title="Different", duration_minutes=10,
                  priority="low",  category="feeding")

    pet.add_task(task_a)
    pet.add_task(task_b)

    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Walk"


def test_filter_by_pet_returns_correct_tasks(owner):
    """filter_by_pet must return only tasks belonging to the named pet."""
    bella  = Pet(id=1, name="Bella",  species="dog", age=3)
    oliver = Pet(id=2, name="Oliver", species="cat", age=5)
    bella.add_task(Task(id=1,  title="Walk",    duration_minutes=30,
                        priority="high", category="exercise"))
    oliver.add_task(Task(id=2, title="Feeding", duration_minutes=5,
                         priority="high", category="feeding"))
    owner.add_pet(bella)
    owner.add_pet(oliver)

    scheduler = Scheduler(owner)
    bella_tasks = scheduler.filter_by_pet("Bella")

    assert len(bella_tasks) == 1
    assert bella_tasks[0].title == "Walk"


def test_filter_by_pet_unknown_name_returns_empty(scheduler):
    """filter_by_pet with a name that does not exist must return an empty list."""
    result = scheduler.filter_by_pet("NonExistent")
    assert result == []
