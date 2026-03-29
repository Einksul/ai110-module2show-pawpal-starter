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
Acts as a collection/manager for all tasks related to a specific pet and owner.
- **Attributes:**
  - `owner` (Owner): The owner responsible for the tasks.
  - `pet` (Pet): The pet receiving the care.
  - `tasks` (List[Task]): A list of care tasks.
- **Methods:**
  - `add_task(task: Task)`: Adds a new care task to the registry.
  - `get_tasks_by_date(date: String) -> List[Task]`: Returns a list of tasks scheduled for a specific date.

### `Task`
Represents an individual pet care action (e.g., walking, feeding).
- **Attributes:**
  - `name` (String): The name of the care task.
  - `duration_minutes` (int): The expected duration of the task in minutes.
  - `date` (String): The date the task needs to be performed (Format: YY/MM/DD).
  - `priority` (int): An integer representing the importance of the task (e.g., 1 is highest priority).
  - `description` (String): A detailed string explaining the task.

---

## Suggested Logic Objects (For Scheduling)

### `SchedulePlanner`
Responsible for evaluating tasks against constraints to create a daily plan.
- **Attributes:**
  - `available_time_minutes` (int): The total time the owner has available to perform tasks.
- **Methods:**
  - `generate_plan(registry: TaskRegistry) -> PlanResult`: Evaluates tasks in the registry, filters by date, sorts by priority/duration, and outputs a planned schedule.

### `PlanResult`
The output of the `SchedulePlanner`. It separates tasks that fit into the available time from those that don't, and provides reasoning.
- **Attributes:**
  - `scheduled_tasks` (List[Task]): The care tasks that made it into the plan based on constraints.
  - `unscheduled_tasks` (List[Task]): The tasks that could not fit into the available time.
  - `explanation` (String): A human-readable description explaining how the planner ranked the tasks and why certain tasks were excluded.