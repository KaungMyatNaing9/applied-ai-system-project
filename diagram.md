# PawPal+ — Class Diagram

```mermaid
classDiagram
    class Owner {
        +String name
        +int daily_available_time
        +List~String~ preferences
        +List~Pet~ pets
        +add_pet(pet: Pet) void
        +remove_pet(petId: int) void
        +get_all_tasks() List~Task~
        +get_pending_tasks() List~Task~
        +get_available_time() int
        +update_preferences(preferences: List~String~) void
    }

    class Pet {
        +int id
        +String name
        +String species
        +int age
        +List~String~ care_needs
        +List~Task~ tasks
        +add_task(task: Task) void
        +remove_task(taskId: int) void
        +get_pending_tasks() List~Task~
        +complete_task(taskId: int, nextTaskId: int) Task
        +get_care_needs() List~String~
        +update_care_needs(needs: List~String~) void
    }

    class Task {
        +int id
        +String title
        +int duration_minutes
        +String priority
        +String category
        +String frequency
        +bool is_completed
        +String time
        +Date due_date
        +mark_complete() void
        +mark_incomplete() void
        +get_next_occurrence(nextId: int) Task
        +update_duration(minutes: int) void
        +update_priority(level: String) void
        +get_details() String
    }

    class Scheduler {
        +Owner owner
        +List~Task~ scheduled_tasks
        +List~String~ conflict_warnings
        +generate_daily_plan() List~Task~
        +organize_by_priority(tasks: List~Task~) List~Task~
        +filter_by_duration(tasks: List~Task~, availableTime: int) List~Task~
        +check_conflicts(task: Task) bool
        +detect_conflicts() List~String~
        +sort_by_time(tasks: List~Task~) List~Task~
        +filter_by_status(completed: bool) List~Task~
        +filter_by_pet(petName: String) List~Task~
        +explain_plan() String
        +get_remaining_time() int
        +reset_plan() void
    }

    Owner "1" *-- "0..*" Pet : owns
    Pet "1" *-- "0..*" Task : has
    Scheduler "1" --> "1" Owner : schedules for
    Scheduler ..> Pet : references
    Scheduler ..> Task : organizes
```

## Relationship Key

| Symbol | Meaning |
|--------|---------|
| `*--`  | Composition — child cannot exist without parent |
| `o--`  | Aggregation — owner holds a reference to tasks |
| `-->`  | Association — scheduler is linked to one owner |
| `..>`  | Dependency — scheduler reads pets/tasks but does not own them |

## Notes

- **Owner → Pet** (composition, 1 to 0..*): Pets belong to one owner and are removed if the owner is deleted. Owner accesses all tasks indirectly through its pets via `get_all_tasks()` and `get_pending_tasks()` — there is no separate owner-level task list.
- **Pet → Task** (composition, 1 to 0..*): Tasks are tied to a specific pet. `complete_task()` marks a task done and automatically appends the next recurrence for recurring tasks.
- **Task — recurring tasks**: The `frequency` field ("once", "daily", "weekly") drives `get_next_occurrence()`, which creates a new Task shifted by the appropriate time delta. This is triggered by `Pet.complete_task()`.
- **Scheduler → Owner** (association): The scheduler is initialized with an owner and uses their available time and preferences to build the plan.
- **Scheduler → Pet / Task** (dependency): The scheduler reads these during `generate_daily_plan()` but does not own or store them directly. After plan generation, `detect_conflicts()` runs automatically and populates `conflict_warnings` with budget overflow, unschedulable tasks, and time-window overlap issues.
