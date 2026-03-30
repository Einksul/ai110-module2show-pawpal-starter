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
        """Sorts a given list of tasks chronologically by date and then time_of_day."""
        return sorted(tasks, key=lambda t: (t.date, t.time_of_day))

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
        """Evaluates tasks, filters by date, and prioritizes based on priority/duration, then time."""
        result = PlanResult()
        
        # 1. Filter tasks for the day
        daily_tasks = registry.filter_tasks(date=date)
        
        def time_to_mins(t_str):
            try:
                h, m = map(int, t_str.split(':'))
                return h * 60 + m
            except ValueError:
                return 0

        # Sort tasks by priority first, then requested time, then duration (shorter first)
        # This ensures higher priority tasks get first pick of their slots, 
        # and for equal priority, earlier requested tasks get processed first.
        ranked_tasks = sorted(daily_tasks, key=lambda t: (t.priority, time_to_mins(t.time_of_day), t.duration_minutes))
        
        occupied_intervals = [] # List of (start, end)
        total_time_used = 0
        
        result.explanation += f"--- Scheduling Plan for {date} ---\n"
        result.explanation += f"Total available free time: {self.available_time_minutes} minutes.\n\n"
        result.explanation += "Ranking Method:\n"
        result.explanation += "1. Priority (1 is highest)\n2. Requested Time\n3. Duration (shortest first to maximize efficiency)\n\n"
        
        for task in ranked_tasks:
            requested_start = time_to_mins(task.time_of_day)
            
            # Find the first available start time >= requested_start
            found_slot = False
            potential_start = requested_start
            
            while not found_slot and potential_start + task.duration_minutes <= 24 * 60:
                conflict = False
                for start, end in occupied_intervals:
                    # Check overlap
                    if not (potential_start + task.duration_minutes <= start or potential_start >= end):
                        conflict = True
                        potential_start = end # Skip past the conflict
                        break
                
                if not conflict:
                    found_slot = True

            # Check global time constraint
            if not found_slot or total_time_used + task.duration_minutes > self.available_time_minutes:
                result.unscheduled_tasks.append(task)
                reason = "Not enough total free time left" if total_time_used + task.duration_minutes > self.available_time_minutes else "Pushed past midnight due to conflicts"
                result.explanation += f"❌ '{task.name}' (Priority {task.priority}):\n   Skipped. {reason}.\n\n"
                continue
                
            # Schedule it!
            scheduled_start_mins = potential_start
            task.scheduled_time = f"{scheduled_start_mins // 60:02d}:{scheduled_start_mins % 60:02d}"
            
            result.scheduled_tasks.append(task)
            occupied_intervals.append((scheduled_start_mins, scheduled_start_mins + task.duration_minutes))
            occupied_intervals.sort() # Keep sorted for efficiency if needed
            total_time_used += task.duration_minutes
            
            if task.scheduled_time != task.time_of_day:
                result.explanation += f"✅ '{task.name}' (Priority {task.priority}):\n   Scheduled for {task.scheduled_time} (Pushed back from {task.time_of_day}).\n\n"
            else:
                result.explanation += f"✅ '{task.name}' (Priority {task.priority}):\n   Scheduled at requested time {task.scheduled_time}.\n\n"

        # Final sort for display
        result.scheduled_tasks.sort(key=lambda t: time_to_mins(getattr(t, 'scheduled_time', t.time_of_day)))
        result.explanation += f"Total time scheduled: {total_time_used} minutes."
        
        return result
