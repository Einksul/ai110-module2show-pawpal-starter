import streamlit as st
import datetime
from pawpal_system import Owner, Pet, Task, TaskRegistry, SchedulePlanner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Initialize Session State ---
# This ensures our backend objects persist across Streamlit button clicks and reruns.
if "system_initialized" not in st.session_state:
    st.session_state.owner = Owner(name="Default Owner")
    st.session_state.pet = Pet(name="Default Pet", animal_type="Dog", owner=st.session_state.owner)
    st.session_state.owner.add_pet(st.session_state.pet)
    
    st.session_state.registry = TaskRegistry(owner=st.session_state.owner)
    st.session_state.system_initialized = True

st.title("🐾 PawPal+")
st.markdown("Welcome to the PawPal+ pet care planning assistant.")

st.divider()

# --- Section 1: Owner and Pet Info ---
st.subheader("1. Profile Information")

col1, col2, col3 = st.columns(3)
with col1:
    new_owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
with col2:
    new_pet_name = st.text_input("Pet name", value=st.session_state.pet.name)
with col3:
    # Set the index based on current pet type
    species_options = ["Dog", "Cat", "Bird", "Other"]
    current_species = st.session_state.pet.animal_type
    species_idx = species_options.index(current_species) if current_species in species_options else 3
    new_species = st.selectbox("Species", species_options, index=species_idx)

# Update backend objects if the text inputs changed
if new_owner_name != st.session_state.owner.name:
    st.session_state.owner.name = new_owner_name
if new_pet_name != st.session_state.pet.name:
    st.session_state.pet.name = new_pet_name
if new_species != st.session_state.pet.animal_type:
    st.session_state.pet.animal_type = new_species

st.divider()

# --- Section 2: Task Management ---
st.subheader("2. Manage Tasks")
st.caption("Add tasks for your pet. They will be saved to your task registry.")

with st.form("add_task_form"):
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        task_name = st.text_input("Task Title", placeholder="e.g., Morning Walk")
        task_date = st.date_input("Date", value=datetime.date.today())
        task_time = st.time_input("Time of Day", value=datetime.time(8, 0))
    with t_col2:
        task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
        # We will use 1 (Highest) to 3 (Lowest) for priority internally
        priority_label = st.selectbox("Priority", ["1 - High", "2 - Medium", "3 - Low"], index=1)
        task_repeat = st.selectbox("Repeat Every (Days)", [0, 1, 2, 3, 4, 5, 6, 7], index=0, format_func=lambda x: "None" if x == 0 else f"{x} day(s)")

    task_desc = st.text_area("Description", placeholder="Optional details...")
    
    submit_task = st.form_submit_button("Add Task")

    if submit_task:
        if not task_name:
            st.error("Please provide a task title.")
        else:
            # Parse Priority ("1 - High" -> 1)
            priority_val = int(priority_label.split(" ")[0])
            repeat_val = task_repeat if task_repeat > 0 else None
            
            # Create actual Task object and add to registry
            new_task = Task(
                name=task_name,
                duration_minutes=int(task_duration),
                date=task_date,
                time_of_day=task_time.strftime("%H:%M"),
                priority=priority_val,
                description=task_desc,
                pet=st.session_state.pet,
                repeat_every_days=repeat_val
            )
            st.session_state.registry.add_task(new_task)
            st.success(f"Added task: {task_name}")

# Display current tasks from the backend registry
if st.session_state.registry.tasks:
    st.write("**Current Tasks in Registry:**")
    for t in st.session_state.registry.tasks:
        repeat_badge = f" 🔁 {t.repeat_every_days} day(s)" if t.repeat_every_days else ""
        with st.expander(f"[{t.priority}] {t.name} on {t.date} at {t.time_of_day} ({t.duration_minutes}m) {repeat_badge}"):
            st.write(f"**For Pet:** {t.pet.name}")
            if t.description:
                st.write(f"**Description:** {t.description}")
            
            # We can add a "Mark Complete" button right here for interactivity!
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Mark Complete", key=f"complete_{t.id}"):
                    t.mark_complete(st.session_state.registry)
                    st.session_state.registry.clean_up()
                    st.rerun() # Refresh the UI to hide the completed task
            with btn_col2:
                if st.button("Delete Task", key=f"delete_{t.id}", type="primary"):
                    st.session_state.registry.remove_task(t.id)
                    st.rerun() # Refresh the UI to remove the task
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Section 3: Scheduling ---
st.subheader("3. Build Daily Schedule")
st.caption("Plan your day based on available time.")

schedule_date = st.date_input("Date to Schedule", value=datetime.date.today(), key="schedule_date")
available_time = st.number_input("Available Free Time (minutes)", min_value=10, max_value=1440, value=120)

if st.button("Generate Schedule"):
    # Soon this will actually call the SchedulePlanner logic
    st.warning("Not implemented yet! We need to write the `generate_plan` logic in `pawpal_system.py` next.")
    
    # st.session_state.planner = SchedulePlanner(available_time_minutes=int(available_time))
    # result = st.session_state.planner.generate_plan(st.session_state.registry, schedule_date)
    # ... display result ...
