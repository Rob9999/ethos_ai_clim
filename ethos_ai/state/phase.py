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
        obj._value_ = auto()  # Automatisch generierter Wert, falls benötigt
        obj.display_name = display_name
        obj.description = description
        obj.duration = duration
        obj.priority = priority
        obj.next_phase = None
        return obj

    def __str__(self) -> str:
        # Liefert den Anzeigenamen der Phase zurück
        return self.display_name

    def __repr__(self) -> str:
        # Liefert eine detaillierte Repräsentation der Phase für Debugging-Zwecke
        return f"<Phase.{self.name}: {self.display_name}>"

    def set_next_phase(self, next_phase: "Phase"):
        # Setzt die nächste Phase, stellt sicher, dass es sich um ein Phase-Enum-Mitglied handelt
        if isinstance(next_phase, Phase):
            self.next_phase = next_phase
        else:
            raise ValueError("next_phase muss ein Mitglied der Phase-Enum sein.")

    def next(self) -> "Phase":
        # Gibt die nächste Phase zurück
        return self.next_phase

    def get_priority(self) -> "Priority":
        return self.priority

    def get_duration(self) -> int:
        return self.duration

    # Phasen-Definitionen
    DREAMING = ("Träumen", "In dieser Phase träumt der Mensch.", 0)
    SLEEPING = ("Schlafen", "In dieser Phase schläft der Mensch.", 0)
    WAKING = ("Aufwachen", "In dieser Phase wacht der Mensch auf.", 0)
    THINKING = ("Denken", "In dieser Phase denkt der Mensch.", 0)
    ACTING = ("Handeln", "In dieser Phase handelt der Mensch.", 0)
    REFLECTING = ("Reflektieren", "In dieser Phase reflektiert der Mensch.", 0)
    OFF = ("Aus", "In dieser Phase ist der Mensch aus.", 0)
    INITIALIZING = (
        "Initialisierung",
        "In dieser Phase wird das Modell initialisiert.",
        0,
    )
    LEARNING = ("Lernen", "In dieser Phase lernt der Mensch.", 0)
    ETHICAL_LEARNING = ("Ethik lernen", "In dieser Phase lernt der Mensch Ethik.", 0)
    DEVIATION_CHECK = (
        "Abweichungen prüfen",
        "In dieser Phase prüft der Mensch Abweichungen.",
        0,
    )
    RUNNING = ("Laufen", "In dieser Phase läuft der Mensch.", 0)
    STARTING = ("Starten", "In dieser Phase startet der Mensch.", 0)
    STOPPING = ("Stoppen", "In dieser Phase stoppt der Mensch.", 0)
    ADVICE = ("Beratung", "In dieser Phase wird der Mensch beraten.", 0)
    EXECUTION = ("Ausführung", "In dieser Phase wird eine Aufgabe ausgeführt.", 0)
    REQUEST = ("Anfrage", "In dieser Phase wird eine Anfrage gestellt.", 0)
    DECISION = ("Entscheidung", "In dieser Phase wird eine Entscheidung getroffen.", 0)
    HANDLE_PRIORITY_1_TASKS = (
        "Priorität 1 Aufgaben bearbeiten",
        "In dieser Phase werden Priorität 1 Aufgaben bearbeitet.",
        0,
        Priority.PRIO_1,
    )
    HANDLE_PRIORITY_2_TASKS = (
        "Priorität 2 Aufgaben bearbeiten",
        "In dieser Phase werden Priorität 2 Aufgaben bearbeitet.",
        0,
        Priority.PRIO_2,
    )
    HANDLE_PRIORITY_LOW_TASKS = (
        "Niedrigpriorisierte Aufgaben bearbeiten",
        "In dieser Phase werden niedrigpriorisierte Aufgaben bearbeitet.",
        0,
        Priority.PRIO_LOW,
    )
    NORMAL_OPERATION = ("Normalbetrieb", "In dieser Phase wird normal gearbeitet.", 0)
    EMERGENCY = (
        "Notfall",
        "In dieser Phase wird ein Notfall behandelt.",
        0,
        Priority.EMERGENCY,
    )
    TRAINING_ETHICS = ("Ethik trainieren", "In dieser Phase wird Ethik trainiert.", 0)
    TRAINING_INDIVIDUAL = (
        "Individuum trainieren",
        "In dieser Phase wird das Individuum trainiert.",
        0,
    )
    TRAINING_CLIM = ("CLIM trainieren", "In dieser Phase wird CLIM trainiert.", 0)
    MAINTENANCE = ("Wartung", "In dieser Phase wird Wartung durchgeführt.", 0)


# Festlegen der nächsten Phasen
Phase.DREAMING.set_next_phase(Phase.SLEEPING)
Phase.SLEEPING.set_next_phase(Phase.WAKING)
Phase.WAKING.set_next_phase(Phase.DREAMING)
Phase.THINKING.set_next_phase(Phase.ACTING)
Phase.ACTING.set_next_phase(Phase.THINKING)
Phase.REFLECTING.set_next_phase(Phase.DREAMING)
Phase.OFF.set_next_phase(Phase.DREAMING)
Phase.INITIALIZING.set_next_phase(Phase.DREAMING)
Phase.LEARNING.set_next_phase(Phase.DREAMING)
Phase.ETHICAL_LEARNING.set_next_phase(Phase.DREAMING)
Phase.DEVIATION_CHECK.set_next_phase(Phase.DREAMING)
Phase.RUNNING.set_next_phase(Phase.DREAMING)
Phase.STOPPING.set_next_phase(Phase.OFF)
Phase.ADVICE.set_next_phase(Phase.DREAMING)
Phase.EXECUTION.set_next_phase(Phase.DREAMING)
Phase.REQUEST.set_next_phase(Phase.DREAMING)
Phase.DECISION.set_next_phase(Phase.DREAMING)
Phase.HANDLE_PRIORITY_1_TASKS.set_next_phase(Phase.DREAMING)
Phase.HANDLE_PRIORITY_2_TASKS.set_next_phase(Phase.DREAMING)
Phase.HANDLE_PRIORITY_LOW_TASKS.set_next_phase(Phase.DREAMING)
Phase.NORMAL_OPERATION.set_next_phase(Phase.DREAMING)
Phase.EMERGENCY.set_next_phase(Phase.DREAMING)
Phase.TRAINING_ETHICS.set_next_phase(Phase.DREAMING)
Phase.TRAINING_INDIVIDUAL.set_next_phase(Phase.DREAMING)
Phase.TRAINING_CLIM.set_next_phase(Phase.DREAMING)
Phase.MAINTENANCE.set_next_phase(Phase.DREAMING)
