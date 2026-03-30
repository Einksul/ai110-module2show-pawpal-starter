import unittest
import datetime
import os
import sys

# Ensure the parent directory is in the sys.path so we can import pawpal_system
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pawpal_system import Owner, Pet, Task, TaskRegistry

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

if __name__ == '__main__':
    unittest.main()
