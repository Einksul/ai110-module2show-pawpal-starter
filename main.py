import datetime
from pawpal_system import Owner, Pet, Task, TaskRegistry

def main():
    print("--- PawPal+ Basic Logic Test ---\n")

    # 1. Create an Owner
    owner = Owner(name="Patrick")
    print(f"Created Owner: {owner.name}")

    # 2. Create Pets and add them to the Owner
    pet1 = Pet(name="Buddy", animal_type="Dog", owner=owner)
    pet2 = Pet(name="Luna", animal_type="Cat", owner=owner)
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    print(f"\n{owner.name}'s Pets:")
    for pet in owner.pets:
        print(f" - {pet.name} ({pet.animal_type})")

    # 3. Create a TaskRegistry for the Owner
    registry = TaskRegistry(owner=owner)
    print("\nCreated Task Registry.")

    # 4. Create Tasks
    today = datetime.date.today()
    
    # Task for Buddy (Dog) - simple walk
    task1 = Task(
        name="Morning Walk",
        duration_minutes=30,
        date=today,
        time_of_day="08:00",
        priority=1,
        description="Brisk walk around the park.",
        pet=pet1
    )
    
    # Task for Buddy - repeating feeding
    task2 = Task(
        name="Feed Buddy",
        duration_minutes=10,
        date=today,
        time_of_day="09:00",
        priority=1,
        description="Give Buddy his dry food.",
        pet=pet1,
        repeat_every_days=1 # Repeats every 1 day
    )

    # Task for Luna (Cat) - grooming
    task3 = Task(
        name="Brush Luna",
        duration_minutes=15,
        date=today,
        time_of_day="18:00",
        priority=2,
        description="Brush Luna's coat to prevent matting.",
        pet=pet2
    )

    # Add tasks to registry
    registry.add_task(task1)
    registry.add_task(task2)
    registry.add_task(task3)

    print(f"\nTasks in Registry (Total: {len(registry.tasks)}):")
    for t in registry.tasks:
        repeat_str = f" (Repeats every {t.repeat_every_days} days)" if t.repeat_every_days else ""
        print(f" - [{t.id[:8]}...] {t.pet.name}: {t.name} at {t.time_of_day} ({t.duration_minutes}m) - Priority {t.priority}{repeat_str}")

    # 5. Test completing a repeating task
    print("\n--- Testing Task Completion ---")
    print(f"Marking '{task2.name}' as complete...")
    task2.mark_complete(registry)
    
    print("Running registry.clean_up() to remove completed tasks...")
    registry.clean_up()

    print(f"\nTasks in Registry after cleanup (Total: {len(registry.tasks)}):")
    for t in registry.tasks:
        repeat_str = f" (Repeats every {t.repeat_every_days} days)" if t.repeat_every_days else ""
        print(f" - [{t.id[:8]}...] {t.pet.name}: {t.name} on {t.date} at {t.time_of_day} ({t.duration_minutes}m){repeat_str}")

if __name__ == "__main__":
    main()
