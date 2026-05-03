"""
main.py
Demonstrates scheduling conflict detection in PawPal+.

Several tasks are intentionally given overlapping time windows so that
the Scheduler's conflict detection can be clearly observed.

Run with:
    python main.py
"""

import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    width = 62
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_schedule(plan: list[Task], pet_map: dict[int, str]) -> None:
    """Print the scheduled task list in a tabular format."""
    if not plan:
        print("  (no tasks scheduled)")
        return
    header = f"  {'#':<4} {'Pet':<10} {'Task':<24} {'Start':>6}  {'Dur':>5}  {'Priority'}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for i, task in enumerate(plan, 1):
        time_str = task.time if task.time else "—"
        pet_name = pet_map.get(task.id, "?")
        print(
            f"  {i:<4} {pet_name:<10} {task.title:<24} "
            f"{time_str:>6}  {task.duration_minutes:>4} min  {task.priority}"
        )


def print_warnings(warnings: list[str]) -> None:
    """Print conflict warnings, or a clean confirmation if none exist."""
    if not warnings:
        print("  No conflicts detected — plan looks clean.")
        return
    for i, msg in enumerate(warnings, 1):
        print(f"  {i}. {msg}")


# ---------------------------------------------------------------------------
# 1. Owner
# ---------------------------------------------------------------------------

owner = Owner(
    name="Alex",
    daily_available_time=90,
    preferences=["high-priority tasks first"],
)

today = datetime.date.today()

# ---------------------------------------------------------------------------
# 2. Bella the dog — tasks with deliberately conflicting time windows
#
#   Morning Walk  07:00 → 07:30  (30 min)
#   Breakfast     07:15 → 07:25  (10 min)  ← overlaps Morning Walk (same pet)
#   Dental Chew   09:00 → 09:05  ( 5 min)
#   Training      09:00 → 09:20  (20 min)  ← overlaps Dental Chew (same pet)
# ---------------------------------------------------------------------------

bella = Pet(id=1, name="Bella", species="dog", age=3,
            care_needs=["daily exercise", "evening feeding"])

bella.add_task(Task(id=1, title="Morning Walk",
                    duration_minutes=30, priority="high",
                    category="exercise", frequency="daily",
                    time="07:00", due_date=today))

bella.add_task(Task(id=2, title="Breakfast",
                    duration_minutes=10, priority="high",
                    category="feeding", frequency="daily",
                    time="07:15",            # starts inside Morning Walk's window
                    due_date=today))

bella.add_task(Task(id=3, title="Dental Chew",
                    duration_minutes=5, priority="medium",
                    category="grooming", frequency="daily",
                    time="09:00", due_date=today))

bella.add_task(Task(id=4, title="Obedience Training",
                    duration_minutes=20, priority="medium",
                    category="exercise", frequency="daily",
                    time="09:00",            # same start as Dental Chew
                    due_date=today))

# ---------------------------------------------------------------------------
# 3. Oliver the cat — one task that overlaps with a Bella task (cross-pet)
#
#   Feeding       07:00 → 07:05  ( 5 min)  ← overlaps Morning Walk (cross-pet)
#   Litter Clean  10:00 → 10:10  (10 min)
#   Playtime      10:05 → 10:20  (15 min)  ← overlaps Litter Clean (same pet)
# ---------------------------------------------------------------------------

oliver = Pet(id=2, name="Oliver", species="cat", age=5,
             care_needs=["weekly brushing", "indoor enrichment"])

oliver.add_task(Task(id=5, title="Feeding",
                     duration_minutes=5, priority="high",
                     category="feeding", frequency="daily",
                     time="07:00",           # same slot as Morning Walk (cross-pet)
                     due_date=today))

oliver.add_task(Task(id=6, title="Litter Box Clean",
                     duration_minutes=10, priority="high",
                     category="hygiene", frequency="daily",
                     time="10:00", due_date=today))

oliver.add_task(Task(id=7, title="Playtime",
                     duration_minutes=15, priority="low",
                     category="exercise", frequency="daily",
                     time="10:05",           # starts inside Litter Clean's window
                     due_date=today))

# ---------------------------------------------------------------------------
# 4. Register pets; build a task → pet name lookup for display
# ---------------------------------------------------------------------------

owner.add_pet(bella)
owner.add_pet(oliver)

task_pet_map: dict[int, str] = {
    task.id: pet.name
    for pet in owner.pets
    for task in pet.tasks
}

# ---------------------------------------------------------------------------
# 5. Show all tasks before scheduling
# ---------------------------------------------------------------------------

print_section("All Registered Tasks (pre-schedule)")

for pet in owner.pets:
    print(f"\n  {pet.name} ({pet.species.capitalize()}, age {pet.age})")
    header = f"    {'ID':<4} {'Task':<24} {'Start':>6}  {'Dur':>5}  {'Priority'}"
    print(header)
    print("    " + "-" * (len(header) - 4))
    for t in pet.tasks:
        time_str = t.time if t.time else "—"
        print(f"    {t.id:<4} {t.title:<24} {time_str:>6}  {t.duration_minutes:>4} min  {t.priority}")

# ---------------------------------------------------------------------------
# 6. Generate the daily plan (conflict detection runs automatically)
# ---------------------------------------------------------------------------

scheduler = Scheduler(owner)
plan = scheduler.generate_daily_plan()

# ---------------------------------------------------------------------------
# 7. Print the generated schedule
# ---------------------------------------------------------------------------

print_section("Generated Daily Schedule")

budget    = owner.get_available_time()
used_time = sum(t.duration_minutes for t in plan)
remaining = scheduler.get_remaining_time()

print(f"\n  Owner   : {owner.name}")
print(f"  Budget  : {budget} min available")
print(f"  Planned : {used_time} min across {len(plan)} task(s)")
print(f"  Free    : {remaining} min unscheduled\n")

print_schedule(plan, task_pet_map)

# ---------------------------------------------------------------------------
# 8. Print conflict warnings (auto-populated by generate_daily_plan)
# ---------------------------------------------------------------------------

print_section("Conflict Warnings")
print()
print_warnings(scheduler.conflict_warnings)

# ---------------------------------------------------------------------------
# 9. Explain why each task was chosen and in what order
# ---------------------------------------------------------------------------

print_section("Scheduling Rationale")
print()
print(scheduler.explain_plan())
