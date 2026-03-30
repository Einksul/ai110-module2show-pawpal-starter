import datetime
from pawpal_system import Owner, Pet, Task, TaskRegistry, SchedulePlanner

def test_priority_conflict_rescheduling():
    owner = Owner("Test Owner")
    pet = Pet("Test Pet", "Dog", owner)
    registry = TaskRegistry(owner)
    
    today = datetime.date.today()
    
    # Task A: Priority 2, 08:30 - 09:30 (60 mins)
    task_a = Task(
        name="Task A",
        duration_minutes=60,
        date=today,
        time_of_day="08:30",
        priority=2,
        description="Lower priority",
        pet=pet
    )
    
    # Task B: Priority 1, 09:15 - 10:00 (45 mins)
    task_b = Task(
        name="Task B",
        duration_minutes=45,
        date=today,
        time_of_day="09:15",
        priority=1,
        description="Higher priority",
        pet=pet
    )
    
    registry.add_task(task_a)
    registry.add_task(task_b)
    
    # Give enough time for both: 60 + 45 = 105 mins. Let's give 200.
    planner = SchedulePlanner(available_time_minutes=200)
    result = test_result = planner.generate_plan(registry, today)
    
    # Check if Task B is at 09:15 (its requested time)
    # Check if Task A is rescheduled (likely to 10:00)
    
    scheduled_tasks = {t.name: t for t in result.scheduled_tasks}
    
    assert "Task B" in scheduled_tasks
    assert "Task A" in scheduled_tasks
    
    # In the current (buggy) implementation, Task A starts at 08:30 and Task B is pushed to 09:30.
    # We WANT Task B at 09:15 and Task A pushed.
    
    print(f"\nTask B scheduled time: {scheduled_tasks['Task B'].scheduled_time}")
    print(f"Task A scheduled time: {scheduled_tasks['Task A'].scheduled_time}")
    
    assert scheduled_tasks['Task B'].scheduled_time == "09:15"
    assert scheduled_tasks['Task A'].scheduled_time == "10:00"

if __name__ == "__main__":
    try:
        test_priority_conflict_rescheduling()
        print("Test passed!")
    except AssertionError as e:
        print(f"Test failed!")
        import traceback
        traceback.print_exc()
