# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My UML design includes four main classes: Owner, Pet, Task, and Scheduler. 
Task - the atomic unit of work. It represents a single pet care activity (e.g., feeding, grooming) and holds data like duration, priority, category, and completion status. Its methods manage its own state: marking itself complete/incomplete, updating duration or priority, and producing a human-readable summary via get_details().

Pet - models an individual pet and owns the tasks specific to that animal's care. It holds the pet's identity (name, species, age) and a care_needs list describing what the pet requires. Its methods let you attach or detach tasks and read or replace care needs. Because tasks are stored directly on the pet, a pet's task list is removed if the pet is removed (composition).

Owner - the central actor in the domain. It holds a daily_available_time budget, scheduling preferences, a roster of Pet objects, and a master tasks list for cross-pet or non-pet tasks (e.g., "buy supplies"). It manages its own collections with add_pet/remove_pet and add_task/remove_task, and exposes get_available_time() for the scheduler to read.

Scheduler - the planning engine. It is initialized with an Owner and generates a daily plan that fits within the owner's time budget. It sorts tasks by priority (organize_by_priority), trims the list to what fits (filter_by_duration), detects conflicts (check_conflicts), and produces a plain-language rationale (explain_plan). It does not own pets or tasks — it only reads them, keeping its responsibility focused on scheduling logic rather than data management.

The separation of concerns is deliberate: Task and Pet manage their own data, Owner aggregates everything the user controls, and Scheduler is the only class responsible for decision-making logic.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
There is no design change from UML design to implementation. It might be due to me using design as reference while leting AI code the skeleton.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three constraints: time budget, priority, and conflicts. The owner's daily_available_time is the hard limit: filter_by_duration ensures the cumulative task duration never exceeds what is available, and get_remaining_time tracks what is left. Within that budget, organize_by_priority ranks tasks from "high" to "medium" to "low" so the most critical care always gets scheduled first. check_conflicts then acts as a safety gate before any task is added to the final plan. Time was treated as the most important constraint because no matter how high a task's priority is, it simply cannot be done if there is no time for it: priority only matters within the time that exists.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

From my perspective, the scheduler makes a tradeoff by using a simple greedy approach that prioritizes high-priority tasks first instead of trying to find the most optimal combination of tasks. This means it might not always maximize the number of tasks completed within a limited time, but it keeps the logic easy to understand and predictable. I think this is reasonable because, in real life, pet owners usually think in terms of urgency rather than optimization. Also, the number of tasks in this app is small, so the difference between greedy and optimal solutions is not very significant. Keeping the algorithm simple makes it easier to maintain and explain, which is important for a practical application like this.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used Claude Code primarily for code generation and debugging. For code generation, I provided detailed prompts describing the functionality I wanted for each class and method, and the AI generated the initial code based on those prompts. This helped me quickly get a working version of the scheduler and its components. I also prompt it to comment on the generated code for better understanding. For debugging, I used AI to analyze error messages and suggest fixes when I encountered issues during testing. The AI's ability to understand the context of my code and provide specific recommendations was invaluable in resolving bugs efficiently.

- What kinds of prompts or questions were most helpful?

The most helpful prompts were those that were specific and detailed about the functionality I wanted. For example, when asking for code generation, I would describe the purpose of the class or method, the inputs it should take, the outputs it should produce, and any specific logic it should follow. This level of detail helped the AI generate code that was closely aligned with my requirements. Additionally, when debugging, providing the exact error message and a brief description of what I was trying to achieve allowed the AI to give more targeted advice.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

There was a moment when the AI suggested a way to handle task conflicts that involved rescheduling tasks to different time slots. I realized that this approach would add unnecessary complexity to the scheduler and could lead to unpredictable behavior for the user. Instead, I decided to implement a simpler conflict detection mechanism that just flags conflicts without trying to resolve them automatically. This way, the owner can make informed decisions about how to adjust their schedule rather than having the app make changes on their behalf.

- How did you evaluate or verify what the AI suggested?

I evaluated the AI's suggestions by considering the user experience and the overall design of the app. I asked myself whether the proposed solution would be intuitive for pet owners and whether it aligned with the core functionality of the app. I also thought about the potential edge cases and how the suggested approach would handle them. In this case, I concluded that a simpler conflict detection method would be more user-friendly and easier to maintain, which is why I chose to implement that instead of the AI's suggestion.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I tested five areas across 18 tests:

1. **Task sorting** — `sort_by_time` returns tasks in chronological `HH:MM` order, and tasks with no time value always sort to the end.
2. **Recurring tasks** — completing a `daily` task creates a new occurrence due tomorrow; `weekly` creates one due in 7 days; `once` produces no follow-up. The new occurrence is also confirmed to be appended to the pet's task list.
3. **Conflict detection** — same-pet time overlaps are flagged; cross-pet overlaps are labelled `cross-pet`; a task longer than the entire daily budget is reported as unschedulable; non-overlapping tasks produce zero warnings.
4. **Edge cases** — a pet with no tasks, an owner with no pets, all tasks already completed, and a duplicate task ID being silently ignored.
5. **Filtering** — `filter_by_pet` returns only the named pet's tasks; an unknown pet name returns an empty list.

- Why were these tests important?

These tests matter because they cover the decisions the scheduler makes that directly affect the owner's day. Sorting correctness ensures the task list is readable in time order. Recurrence tests verify that daily/weekly care never silently drops off the schedule after being marked complete, a bug there would cause a pet to miss regular care without any visible error. Conflict detection tests ensure the warnings fire precisely when they should and stay silent when there is no real problem, so owners can trust the warnings instead of ignoring them as noise. Edge-case tests protect against crashes on valid but empty inputs (no pets, no tasks, everything done), which are common at the start or end of a real day. Filtering tests confirm that scoping the view to one pet returns only that pet's data, which is the foundation of a multi-pet UI.

**b. Confidence**

- How confident are you that your scheduler works correctly?

**★★★★☆ (4/5).** All 18 tests pass and cover the core behaviours — sorting, recurrence, conflict detection, filtering, and common edge cases. Confidence drops one star because there are no tests for the Streamlit UI layer, raw user string inputs (e.g. malformed `HH:MM`, invalid priority values), or persistent storage. The logic is solid; the boundaries with the outside world are not yet verified.

- What edge cases would you test next if you had more time?

1. **Malformed time strings** — e.g. `"8:5"`, `"25:00"`, or `"abc"` passed as a task's `time` field to ensure `sort_by_time` and `detect_conflicts` don't crash.
2. **Zero available time** — an owner with `daily_available_time = 0` should produce an empty plan without errors.
3. **Two tasks with identical titles but different IDs** — verify `check_conflicts` (which matches on title) behaves as intended.
4. **Completing a task with no `due_date`** — recurrence falls back to `date.today()`; confirm the next occurrence date is still correct.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the overall system design and how well the classes and their responsibilities are defined. The separation of concerns between Task, Pet, Owner, and Scheduler made the implementation straightforward and the code easy to understand. The Scheduler's logic for sorting, filtering by duration, and detecting conflicts is clean and works as intended, which is reflected in the passing test suite. I also appreciate how the tests cover a wide range of scenarios, giving me confidence in the core functionality of the app.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would improve the Scheduler's conflict resolution strategy. Instead of just flagging conflicts, I would implement a more sophisticated approach that suggests alternative time slots for conflicting tasks or allows the user to manually resolve conflicts within the app. This would enhance the user experience by providing actionable insights rather than just warnings. Additionally, I would add validation for user inputs, especially for time formats and priority values, to prevent errors and ensure data integrity from the start.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important takeaway is that while AI can be a powerful tool for generating code and providing suggestions, it's crucial to apply human judgment to evaluate those suggestions in the context of the overall system design and user experience. Not every AI-generated solution will be the best fit for the specific needs of the application, and it's up to the developer to assess whether a suggestion aligns with the goals of the project and the expectations of the users. This project reinforced the importance of maintaining a clear vision for the system's functionality and user experience, even when leveraging AI assistance.
