import unittest
import datetime
import os
import sys

# Ensure the parent directory is in the sys.path so we can import pawpal_system
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pawpal_system import Owner, Pet, Task, TaskRegistry, SchedulePlanner

class TestPawPalSystem(unittest.TestCase):

    def setUp(self):
        """Set up standard objects for testing."""
        self.owner = Owner(name="Patrick")
        self.pet1 = Pet(name="Buddy", animal_type="Dog", owner=self.owner)
        self.pet2 = Pet(name="Luna", animal_type="Cat", owner=self.owner)
        self.owner.add_pet(self.pet1)
        self.owner.add_pet(self.pet2)
        
        self.registry = TaskRegistry(owner=self.owner)
        self.today = datetime.date.today()

    def test_owner_and_pet_creation(self):
        """Test that owner and pets are correctly linked."""
        self.assertEqual(self.owner.name, "Patrick")
        self.assertEqual(len(self.owner.pets), 2)
        self.assertEqual(self.owner.pets[0].name, "Buddy")
        self.assertEqual(self.owner.pets[1].name, "Luna")

    def test_add_and_retrieve_tasks(self):
        """Test adding tasks and filtering them by date."""
        task1 = Task("Morning Walk", 30, self.today, "08:00", 1, "Walk", self.pet1)
        task2 = Task("Feed", 10, self.today, "09:00", 1, "Food", self.pet1)
        
        self.registry.add_task(task1)
        self.registry.add_task(task2)
        
        self.assertEqual(len(self.registry.tasks), 2)
        
        # Test retrieving by date
        tasks_today = self.registry.get_tasks_by_date(self.today)
        self.assertEqual(len(tasks_today), 2)
        
        # Test retrieving by another date
        tomorrow = self.today + datetime.timedelta(days=1)
        tasks_tomorrow = self.registry.get_tasks_by_date(tomorrow)
        self.assertEqual(len(tasks_tomorrow), 0)

    def test_task_completion_and_repetition(self):
        """Test completing a repeating task and cleaning up the registry."""
        task_repeat = Task(
            name="Feed Buddy",
            duration_minutes=10,
            date=self.today,
            time_of_day="09:00",
            priority=1,
            description="Give Buddy his dry food.",
            pet=self.pet1,
            repeat_every_days=1 # Repeats daily
        )
        self.registry.add_task(task_repeat)
        self.assertEqual(len(self.registry.tasks), 1)

        # Mark as complete
        task_repeat.mark_complete(self.registry)
        
        # We should now have the old completed task AND the new future task
        self.assertEqual(len(self.registry.tasks), 2)
        self.assertTrue(self.registry.tasks[0].is_completed)
        self.assertFalse(self.registry.tasks[1].is_completed)
        
        # Verify the new task's date is exactly 1 day later
        new_task = self.registry.tasks[1]
        self.assertEqual(new_task.time_of_day, "09:00")
        self.assertEqual(new_task.date, self.today + datetime.timedelta(days=1))

        # Clean up completed tasks
        self.registry.clean_up()
        self.assertEqual(len(self.registry.tasks), 1)
        self.assertEqual(self.registry.tasks[0].id, new_task.id)

    # --- SCHEDULER TESTS ---

    def test_scheduler_basic_time_constraint(self):
        """Test that tasks exceeding total available time are skipped."""
        task1 = Task("Walk", 60, self.today, "10:00", 1, "", self.pet1)
        task2 = Task("Groom", 40, self.today, "12:00", 1, "", self.pet2)
        self.registry.add_task(task1)
        self.registry.add_task(task2)

        # Only 80 minutes available. Task 1 takes 60, leaving 20. Task 2 needs 40, so it fails.
        planner = SchedulePlanner(available_time_minutes=80)
        result = planner.generate_plan(self.registry, self.today)

        self.assertEqual(len(result.scheduled_tasks), 1)
        self.assertEqual(result.scheduled_tasks[0].name, "Walk")
        self.assertEqual(len(result.unscheduled_tasks), 1)
        self.assertEqual(result.unscheduled_tasks[0].name, "Groom")

    def test_scheduler_priority_and_pushback(self):
        """Test that a timing conflict resolves by priority, pushing the lower priority task back."""
        # Both tasks start at 10:00
        # Task 1: Priority 2 (Medium), 30 mins
        task1 = Task("Play", 30, self.today, "10:00", 2, "", self.pet1)
        # Task 2: Priority 1 (High), 15 mins
        task2 = Task("Meds", 15, self.today, "10:00", 1, "", self.pet1)
        
        self.registry.add_task(task1)
        self.registry.add_task(task2)

        planner = SchedulePlanner(available_time_minutes=120)
        result = planner.generate_plan(self.registry, self.today)

        self.assertEqual(len(result.scheduled_tasks), 2)
        
        # High priority "Meds" should execute right at 10:00
        self.assertEqual(result.scheduled_tasks[0].name, "Meds")
        self.assertEqual(result.scheduled_tasks[0].scheduled_time, "10:00")
        
        # Lower priority "Play" should be pushed back to start right after Meds finishes (10:15)
        self.assertEqual(result.scheduled_tasks[1].name, "Play")
        self.assertEqual(result.scheduled_tasks[1].scheduled_time, "10:15")

    def test_scheduler_duration_tie_breaker(self):
        """Test that conflicts with the SAME priority resolve by favoring the shorter task."""
        # Both start at 14:00, both are Priority 1
        # Task 1: Long (60m)
        task1 = Task("Long Walk", 60, self.today, "14:00", 1, "", self.pet1)
        # Task 2: Short (10m)
        task2 = Task("Quick Feed", 10, self.today, "14:00", 1, "", self.pet2)

        self.registry.add_task(task1)
        self.registry.add_task(task2)

        planner = SchedulePlanner(available_time_minutes=120)
        result = planner.generate_plan(self.registry, self.today)

        self.assertEqual(len(result.scheduled_tasks), 2)
        
        # The shorter task should run first to maximize task completion
        self.assertEqual(result.scheduled_tasks[0].name, "Quick Feed")
        self.assertEqual(result.scheduled_tasks[0].scheduled_time, "14:00")
        
        # The longer task gets pushed back
        self.assertEqual(result.scheduled_tasks[1].name, "Long Walk")
        self.assertEqual(result.scheduled_tasks[1].scheduled_time, "14:10")

    def test_scheduler_past_midnight_exclusion(self):
        """Test that tasks pushed past 23:59 are properly skipped."""
        # High priority task takes up the end of the day
        task1 = Task("Late Event", 120, self.today, "22:30", 1, "", self.pet1)
        # Lower priority task also scheduled for 22:30, takes 60 mins
        task2 = Task("Late Play", 60, self.today, "22:30", 2, "", self.pet2)
        
        self.registry.add_task(task1)
        self.registry.add_task(task2)

        planner = SchedulePlanner(available_time_minutes=500)
        result = planner.generate_plan(self.registry, self.today)

        # task1 goes from 22:30 to 24:30 (past midnight!).
        # Wait, the algorithm starts task1 at 22:30 (1350 mins). 1350 + 120 = 1470 (past 1440).
        # Actually, let's trace: 22:30 is 1350 mins. 1350 + 120 = 1470 mins.
        # It should skip task1 completely because it goes past midnight.
        # If task1 is skipped, task2 will try to schedule at 22:30. 1350 + 60 = 1410 mins. This fits!
        
        self.assertEqual(len(result.unscheduled_tasks), 1)
        self.assertEqual(result.unscheduled_tasks[0].name, "Late Event")
        
        self.assertEqual(len(result.scheduled_tasks), 1)
        self.assertEqual(result.scheduled_tasks[0].name, "Late Play")
        self.assertEqual(result.scheduled_tasks[0].scheduled_time, "22:30")

if __name__ == '__main__':
    unittest.main()
