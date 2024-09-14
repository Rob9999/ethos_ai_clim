from enum import Enum, auto
from ethos_ai.state.priority import Priority


class Phase(Enum):
    def __new__(
        cls,
        display_name: str,
        description: str,
        duration: int,
        priority: "Priority" = Priority.NORMAL,
    ):
        obj = object.__new__(cls)
        obj._value_ = auto()  # Automatically generated value if needed
        obj.display_name = display_name
        obj.description = description
        obj.duration = duration
        obj.priority = priority
        obj.next_phase = None
        return obj

    def __str__(self) -> str:
        # Returns the display name of the phase
        return self.display_name

    def __repr__(self) -> str:
        # Returns a detailed representation of the phase for debugging purposes
        return f"<Phase.{self.name}: {self.display_name}>"

    def set_next_phase(self, next_phase: "Phase"):
        # Sets the next phase, ensures it is a member of the Phase enum
        if isinstance(next_phase, Phase):
            self.next_phase = next_phase
        else:
            raise ValueError("next_phase must be a member of the Phase enum.")

    def next(self) -> "Phase":
        # Returns the next phase
        return self.next_phase

    def get_priority(self) -> "Priority":
        return self.priority

    def get_duration(self) -> int:
        return self.duration

    # Phase definitions
    DREAMING = ("Dreaming", "In this phase, the human is dreaming.", 0)
    SLEEPING = ("Sleeping", "In this phase, the human is sleeping.", 0)
    WAKING = ("Waking", "In this phase, the human is waking up.", 0)
    THINKING = ("Thinking", "In this phase, the human is thinking.", 0)
    ACTING = ("Acting", "In this phase, the human is acting.", 0)
    REFLECTING = ("Reflecting", "In this phase, the human is reflecting.", 0)
    OFF = ("Off", "In this phase, the human is off.", 0)
    INITIALIZING = (
        "Initializing",
        "In this phase, the model is being initialized.",
        0,
    )
    LEARNING = ("Learning", "In this phase, the human is learning.", 0)
    ETHICAL_LEARNING = (
        "Ethical Learning",
        "In this phase, the human learns ethics.",
        0,
    )
    DEVIATION_CHECK = (
        "Checking for Deviations",
        "In this phase, the human checks for deviations.",
        0,
    )
    RUNNING = ("Running", "In this phase, the human is running.", 0)
    STARTING = ("Starting", "In this phase, the human is starting.", 0)
    STOPPING = ("Stopping", "In this phase, the human is stopping.", 0)
    ADVICE = ("Advice", "In this phase, the human is receiving advice.", 0)
    EXECUTION = ("Execution", "In this phase, a task is being executed.", 0)
    REQUEST = ("Request", "In this phase, a request is made.", 0)
    DECISION = ("Decision", "In this phase, a decision is made.", 0)
    HANDLE_PRIORITY_1_TASKS = (
        "Handling Priority 1 Tasks",
        "In this phase, Priority 1 tasks are handled.",
        0,
        Priority.PRIO_1,
    )
    HANDLE_PRIORITY_2_TASKS = (
        "Handling Priority 2 Tasks",
        "In this phase, Priority 2 tasks are handled.",
        0,
        Priority.PRIO_2,
    )
    HANDLE_PRIORITY_LOW_TASKS = (
        "Handling Low Priority Tasks",
        "In this phase, low-priority tasks are handled.",
        0,
        Priority.PRIO_LOW,
    )
    NORMAL_OPERATION = ("Normal Operation", "In this phase, normal work is done.", 0)
    EMERGENCY = (
        "Emergency",
        "In this phase, an emergency is handled.",
        0,
        Priority.EMERGENCY,
    )
    TRAINING_ETHICS = ("Ethics Training", "In this phase, ethics are trained.", 0)
    TRAINING_INDIVIDUAL = (
        "Individual Training",
        "In this phase, the individual is trained.",
        0,
    )
    TRAINING_CLIM = ("CLIM Training", "In this phase, CLIM is trained.", 0)
    MAINTENANCE = ("Maintenance", "In this phase, maintenance is carried out.", 0)


# Set the next phases with more meaningful transitions

# After dreaming, it makes sense to wake up, following the natural sleep cycle.
Phase.DREAMING.set_next_phase(Phase.WAKING)

# Once sleeping is over, the natural next phase is waking up.
Phase.SLEEPING.set_next_phase(Phase.WAKING)

# After waking up, a period of thinking or processing thoughts is natural.
Phase.WAKING.set_next_phase(Phase.THINKING)

# After thinking comes decision-making, where the human resolves how to act.
Phase.THINKING.set_next_phase(Phase.DECISION)

# After a decision is made, the next logical step is to act on it.
Phase.DECISION.set_next_phase(Phase.ACTING)

# After acting, reflection on those actions often follows.
Phase.ACTING.set_next_phase(Phase.REFLECTING)

# Once reflection is complete, the cycle returns to dreaming, closing the loop.
Phase.REFLECTING.set_next_phase(Phase.DREAMING)

# When off, the next phase would naturally be initializing, to turn things on.
Phase.OFF.set_next_phase(Phase.INITIALIZING)

# After initialization, the model is ready for normal operations.
Phase.INITIALIZING.set_next_phase(Phase.NORMAL_OPERATION)

# After learning, the human might transition to training specific skills, like training the individual.
Phase.LEARNING.set_next_phase(Phase.TRAINING_INDIVIDUAL)

# After ethical learning, the human might reflect on what they have learned.
Phase.ETHICAL_LEARNING.set_next_phase(Phase.REFLECTING)

# Once deviations are checked, normal operations resume.
Phase.DEVIATION_CHECK.set_next_phase(Phase.NORMAL_OPERATION)

# After running, it’s useful to reflect on what was achieved during that time.
Phase.RUNNING.set_next_phase(Phase.REFLECTING)

# After stopping, the system is considered off, closing this cycle.
Phase.STOPPING.set_next_phase(Phase.OFF)

# After receiving advice, the next logical step is making a decision based on that advice.
Phase.ADVICE.set_next_phase(Phase.DECISION)

# After executing a task, the human might reflect on the outcome.
Phase.EXECUTION.set_next_phase(Phase.REFLECTING)

# After making a request, a decision is needed about how to proceed.
Phase.REQUEST.set_next_phase(Phase.DECISION)

# After a decision is made, execution of that decision follows.
Phase.DECISION.set_next_phase(Phase.EXECUTION)

# Handling priority 1 tasks should naturally lead to handling lower-priority tasks next.
Phase.HANDLE_PRIORITY_1_TASKS.set_next_phase(Phase.HANDLE_PRIORITY_2_TASKS)

# After priority 2 tasks, low-priority tasks are handled.
Phase.HANDLE_PRIORITY_2_TASKS.set_next_phase(Phase.HANDLE_PRIORITY_LOW_TASKS)

# After all tasks are handled, normal operations resume.
Phase.HANDLE_PRIORITY_LOW_TASKS.set_next_phase(Phase.NORMAL_OPERATION)

# Once normal operations are finished, priority tasks may need to be checked again.
Phase.NORMAL_OPERATION.set_next_phase(Phase.HANDLE_PRIORITY_1_TASKS)

# After an emergency is handled, things go back to normal operations.
Phase.EMERGENCY.set_next_phase(Phase.NORMAL_OPERATION)

# After ethics training, it makes sense to continue ethical learning.
Phase.TRAINING_ETHICS.set_next_phase(Phase.ETHICAL_LEARNING)

# After training the individual, normal operations resume.
Phase.TRAINING_INDIVIDUAL.set_next_phase(Phase.NORMAL_OPERATION)

# After CLIM training, normal operations follow.
Phase.TRAINING_CLIM.set_next_phase(Phase.NORMAL_OPERATION)

# After maintenance is performed, the system returns to running.
Phase.MAINTENANCE.set_next_phase(Phase.RUNNING)
