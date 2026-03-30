# PawPal+ API and Object Documentation

## Core Objects

### `Owner`
Represents a pet owner who uses the application.
- **Attributes:**
  - `name` (String): The name of the owner.
  - `pets` (List[Pet]): A list containing the pets owned by this owner.
- **Methods:**
  - `add_pet(pet: Pet)`: Associates a new pet with the owner.

### `Pet`
Represents a pet that requires care.
- **Attributes:**
  - `name` (String): The name of the pet.
  - `animal_type` (String): The species/type of animal (e.g., Dog, Cat, Bird).
  - `owner` (Owner): A reference to the pet's owner.

### `TaskRegistry`
Acts as a central manager for all tasks related to an owner and all of their pets.
- **Attributes:**
  - `owner` (Owner): The owner responsible for the tasks.
  - `tasks` (List[Task]): A list of all care tasks across all pets.
- **Methods:**
  - `add_task(task: Task)`: Adds a new care task to the registry.
  - `get_tasks_by_date(date: datetime.date) -> List[Task]`: Returns a list of tasks scheduled for a specific date.
  - `remove_task(task_id: String)`: Removes a specific task from the registry by its ID.
  - `clean_up()`: Removes all tasks that are marked as completed from the registry.

### `Task`
Represents an individual pet care action (e.g., walking, feeding).
- **Attributes:**
  - `id` (String): A unique identifier for the task (UUID).
  - `name` (String): The name of the care task.
  - `duration_minutes` (int): The expected duration of the task in minutes.
  - `date` (datetime.date): The date the task needs to be performed.
  - `time_of_day` (String): The specific time or hour of the day the task should be done (e.g., "08:00 AM" or "14:00").
  - `priority` (int): An integer representing the importance of the task.
  - `description` (String): A detailed string explaining the task.
  - `pet` (Pet): A reference to the specific pet this task is for.
  - `repeat_every_minutes` (Optional[int]): How often the task should repeat in minutes (must be strictly greater than duration).
  - `is_completed` (boolean): Indicates whether the task has been finished.
- **Methods:**
  - `mark_complete(registry: TaskRegistry)`: Marks the task as done and, if `repeat_every_minutes` is set, calculates the next occurrence and adds the new task to the given registry.

---

## Suggested Logic Objects (For Scheduling)

### `SchedulePlanner`
Responsible for evaluating tasks against constraints to create a daily plan.
- **Attributes:**
  - `available_time_minutes` (int): The total time the owner has available to perform tasks.
- **Methods:**
  - `generate_plan(registry: TaskRegistry, date: datetime.date) -> PlanResult`: Evaluates tasks in the registry for a given date, sorts by priority/duration, and outputs a planned schedule.

### `PlanResult`
The output of the `SchedulePlanner`. It separates tasks that fit into the available time from those that don't, and provides reasoning.
- **Attributes:**
  - `scheduled_tasks` (List[Task]): The care tasks that made it into the plan based on constraints.
  - `unscheduled_tasks` (List[Task]): The tasks that could not fit into the available time.
  - `explanation` (String): A human-readable description explaining how the planner ranked the tasks and why certain tasks were excluded.