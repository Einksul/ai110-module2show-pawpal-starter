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
    def __init__(self, name: str, duration_minutes: int, date: datetime.date, time_of_day: str, priority: int, description: str, pet: Pet, repeat_every_days: Optional[int] = None):
        if repeat_every_days is not None and repeat_every_days <= 0:
            raise ValueError("Task repetition interval (repeat_every_days) must be greater than 0.")
            
        self.id = str(uuid.uuid4())
        self.name = name
        self.duration_minutes = duration_minutes
        self.date = date
        self.time_of_day = time_of_day
        self.priority = priority
        self.description = description
        self.pet = pet
        self.repeat_every_days = repeat_every_days
        self.is_completed = False

    def mark_complete(self, registry: 'TaskRegistry') -> None:
        """Marks the task as complete and schedules the next occurrence if repeating."""
        self.is_completed = True
        
        if self.repeat_every_days is not None:
            next_date = self.date + datetime.timedelta(days=self.repeat_every_days)
            
            new_task = Task(
                name=self.name,
                duration_minutes=self.duration_minutes,
                date=next_date,
                time_of_day=self.time_of_day,
                priority=self.priority,
                description=self.description,
                pet=self.pet,
                repeat_every_days=self.repeat_every_days
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

    def filter_tasks(self, date: Optional[datetime.date] = None, pet_name: Optional[str] = None, priority: Optional[int] = None) -> List[Task]:
        """Returns a list of tasks filtered by optional criteria."""
        filtered = self.tasks
        if date:
            filtered = [task for task in filtered if task.date == date]
        if pet_name:
            filtered = [task for task in filtered if task.pet.name.lower() == pet_name.lower()]
        if priority:
            filtered = [task for task in filtered if task.priority == priority]
        return filtered

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sorts a given list of tasks chronologically by their time_of_day."""
        return sorted(tasks, key=lambda t: t.time_of_day)

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
        result = PlanResult()
        
        # 1. Filter tasks for the day
        daily_tasks = registry.filter_tasks(date=date)
        
        def time_to_mins(t_str):
            try:
                h, m = map(int, t_str.split(':'))
                return h * 60 + m
            except ValueError:
                return 0

        # Sort all daily tasks chronologically by their original requested time
        pending_tasks = sorted(daily_tasks, key=lambda t: time_to_mins(t.time_of_day))
        
        ready_queue = []
        current_time_mins = 0
        total_time_used = 0
        
        result.explanation += f"--- Scheduling Plan for {date} ---\n"
        result.explanation += f"Total available free time: {self.available_time_minutes} minutes.\n\n"
        
        while pending_tasks or ready_queue:
            # If no tasks are ready, jump time forward to the next pending task
            if not ready_queue:
                next_task_time = time_to_mins(pending_tasks[0].time_of_day)
                if current_time_mins < next_task_time:
                    current_time_mins = next_task_time
                    
            # Move all tasks whose requested time has arrived into the ready queue
            while pending_tasks and time_to_mins(pending_tasks[0].time_of_day) <= current_time_mins:
                ready_queue.append(pending_tasks.pop(0))
                
            # Sort the ready queue by priority (1 is highest), then duration (shortest first)
            # This ensures we ONLY use priority to resolve actual timing conflicts
            ready_queue.sort(key=lambda t: (t.priority, t.duration_minutes))
            
            task = ready_queue.pop(0)
            
            # Check global time constraint
            if total_time_used + task.duration_minutes > self.available_time_minutes:
                result.unscheduled_tasks.append(task)
                result.explanation += f"❌ '{task.name}': Skipped. Not enough total free time left (Needs {task.duration_minutes}m, only {self.available_time_minutes - total_time_used}m available).\n"
                continue
                
            # Check if pushing back puts it past midnight
            if current_time_mins + task.duration_minutes > 24 * 60:
                result.unscheduled_tasks.append(task)
                result.explanation += f"❌ '{task.name}': Skipped. Pushed past midnight due to conflicts.\n"
                continue
                
            # Schedule it! We dynamically add `scheduled_time` so we don't mutate the original `time_of_day`
            task.scheduled_time = f"{current_time_mins // 60:02d}:{current_time_mins % 60:02d}"
            result.scheduled_tasks.append(task)
            total_time_used += task.duration_minutes
            
            if task.scheduled_time != task.time_of_day:
                result.explanation += f"✅ '{task.name}' (Priority {task.priority}): Scheduled for {task.scheduled_time} (Pushed back from {task.time_of_day}).\n"
            else:
                result.explanation += f"✅ '{task.name}' (Priority {task.priority}): Scheduled at requested time {task.scheduled_time}.\n"
                
            # Advance current time to the end of this task
            current_time_mins += task.duration_minutes

        result.explanation += f"\nTotal time scheduled: {total_time_used} minutes."
        
        return result
