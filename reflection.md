# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

There are 4 major classes:
- Owner: This contains the name of the owner and all the pets they own
- Pet: This contains teh name of the animal, its name, and the owner it is assigned to 
- Task: this is a task with the info for the task. The priority, the time of the task, and the description of the task 
- Task planner: this takes all the task object and has methods to organize and output a schedule 

In the UML document, it is explained the relationships. The pet is owned by the owner, the owner owns the pet, the task scheudler points to the owner and the specific tasks.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
yes, gemini noted that tasks planner was not exposed to all the pets the owner owned, so it would be unable to optimize all tasks that the owner had. Thus, the task planner class was changed to be owned by the owner as well and see all tasks that the owner had. Additionally a unique ID was assigned to the tasks, thus if a specific task, like walking, happens multiple times a day we will be able to differentiate it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler consideres priority and time. If there are no conflicts at the desired time and for the desired length the scheudler puts the task in. If there is a conflict it uses priority as the first tie breaker. Then it optimizes for time. Tasks with lower time are preferred. When there is a timing conflict. The task that has a lower priority gets pushed backed to the next available time slot. If no timeslots are available then the task is skipped and a warning message is sent

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

When there is not enough time to fit everything. The scheduler drops the longer tasks, priority being equal. This is because implicitly we are trying to save the most time. So we favor tasks that are shorter, priority being equal.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI for brainstorming, refactoring the code, and understanding the frameworks. The best responses were when the AI and I were having a discussion and clarifying intent. When there was confusion, espeically with the scheduler logic on which things should be prioritized, asking what its thought process was and having it repeat what it thought the goal was was helpful. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

At first the AI did not understand the intent of the scheduler and was returning the schedule in priority order. This made a confusing schedule. I had to ask it to explain its understanding of the and what it thought it had to do. I then re-explained what I wanted.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the UI and classes breifly. I added tests to add multiple pets to an owner, adding multiple tasks, testing the repeating logic for tasks, and verifying that the pet constructor is correctly called and populates the correct data.

Where most of the testing went was in the scheduler logic. I tested the linear probing for task collisions, correctly prioritizes shorter tasks, and higher priority tasks, and also failed tasks (not enough time). Most of the tests were dedicated to this as this is the main function of the project. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I am relatively confident this works correctly. I would test more on the repeating tasks, as dealing with marking them as complete could introduce some extra errors. 
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I was satisfied with being able to quickly design and put together a functioning app. While I know I could code each part individually, and am confident enough in algorithms to do the scheduler indpendently. Having a sort of teammate to create something quickly was satisfying.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would definitely improve the UI. At this point it is still barebones. Additionally I would like to add a feature to specify when the free time blocks are and have the scheduler plan around that. Finally, I would like to add multiple users and have some sort of saving a loading logic, so that you don't have to reinput the tasks everytime you spin the app. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

You still have to be the architect when you are building the system. Do not off load critical thinking to the ai. You still have to guide it and explain what it should be doing to get the most out of it.
