from typing import List, Optional
import datetime
import uuid

class Pet:
    """Represents a pet that requires care."""
    def __init__(self, name: str, animal_type: str, owner: 'Owner'):
        self.name = name
        self.animal_type = animal_type
        self.owner = owner

class Owner:
    """Represents a pet owner who uses the application."""
    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Associates a new pet with the owner."""
        self.pets.append(pet)

class Task:
    """Represents an individual pet care action."""
    def __init__(self, name: str, duration_minutes: int, date: datetime.date, time_of_day: str, priority: int, description: str, pet: Pet, repeat_every_minutes: Optional[int] = None):
        if repeat_every_minutes is not None and repeat_every_minutes <= duration_minutes:
            raise ValueError("Task repetition interval (repeat_every_minutes) must be strictly greater than its duration.")
            
        self.id = str(uuid.uuid4())
        self.name = name
        self.duration_minutes = duration_minutes
        self.date = date
        self.time_of_day = time_of_day
        self.priority = priority
        self.description = description
        self.pet = pet
        self.repeat_every_minutes = repeat_every_minutes
        self.is_completed = False

    def mark_complete(self, registry: 'TaskRegistry') -> None:
        """Marks the task as complete and schedules the next occurrence if repeating."""
        self.is_completed = True
        
        if self.repeat_every_minutes is not None:
            # Parse the time_of_day to perform datetime math. We assume "HH:MM" format.
            try:
                time_obj = datetime.datetime.strptime(self.time_of_day, "%H:%M").time()
            except ValueError:
                # Fallback to 00:00 if the format doesn't match
                time_obj = datetime.time(0, 0)
                
            current_datetime = datetime.datetime.combine(self.date, time_obj)
            next_datetime = current_datetime + datetime.timedelta(minutes=self.repeat_every_minutes)
            
            new_task = Task(
                name=self.name,
                duration_minutes=self.duration_minutes,
                date=next_datetime.date(),
                time_of_day=next_datetime.strftime("%H:%M"),
                priority=self.priority,
                description=self.description,
                pet=self.pet,
                repeat_every_minutes=self.repeat_every_minutes
            )
            registry.add_task(new_task)

class TaskRegistry:
    """Acts as a collection/manager for all tasks related to an owner and all their pets."""
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Adds a new care task to the registry."""
        self.tasks.append(task)

    def get_tasks_by_date(self, date: datetime.date) -> List[Task]:
        """Returns a list of tasks scheduled for a specific date."""
        return [task for task in self.tasks if task.date == date]

    def remove_task(self, task_id: str) -> None:
        """Removes a task from the registry by its ID (useful for cancelling future repeating tasks)."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def clean_up(self) -> None:
        """Removes all completed tasks from the registry."""
        self.tasks = [task for task in self.tasks if not task.is_completed]

class PlanResult:
    """The output of the SchedulePlanner."""
    def __init__(self):
        self.scheduled_tasks: List[Task] = []
        self.unscheduled_tasks: List[Task] = []
        self.explanation: str = ""

class SchedulePlanner:
    """Responsible for evaluating tasks against constraints to create a daily plan."""
    def __init__(self, available_time_minutes: int):
        self.available_time_minutes = available_time_minutes

    def generate_plan(self, registry: TaskRegistry, date: datetime.date) -> PlanResult:
        """Evaluates tasks, filters by date, sorts by priority/duration, and outputs a planned schedule."""
        pass
