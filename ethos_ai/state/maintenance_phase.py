from enum import Enum, auto

class MaintenancePhase(Enum):

    # MaintenancePhase-Definitionen
    NONE = ("Keine Maintenance", "Keine Maintenance.", 0)
    HANDLING_PRIORITY_1_TASKS = ("Priorität 1 Maintenance", "In dieser Phase werden Priorität 1 Maintenance Aufgaben bearbeitet.", 0)
    HANDLING_PRIORITY_2_TASKS = ("Priorität 2 Maintenance", "In dieser Phase werden Priorität 2 MaintenanceAufgaben bearbeitet.", 0)
    HANDLING_PRIORITY_LOW_TASKS = ("Priorität Niedrig Maintenance", "In dieser Phase werden niedrig priorisierte Maintenance Aufgaben bearbeitet.", 0)
    CHECKING_FOR_PRIO_1_TASKS = ("Priorität 1 Maintenance prüfen", "In dieser Phase wird geprüft, ob Priorität 1 Maintenance Aufgaben anfallen.", 0)
    CHECKING_FOR_PRIO_2_TASKS = ("Priorität 2 Maintenance prüfen", "In dieser Phase wird geprüft, ob Priorität 2 Maintenance Aufgaben anfallen.", 0)
    CHECKING_FOR_PRIO_LOW_TASKS = ("Priorität Niedrig Maintenance prüfen", "In dieser Phase wird geprüft, ob niedrig priorisierte Maintenance Aufgaben anfallen.", 0)

    def __new__(cls, display_name: str, description: str, duration: int):
        obj = object.__new__(cls)
        obj._value_ = auto()  # Automatisch generierter Wert, falls benötigt
        obj.display_name = display_name
        obj.description = description
        obj.duration = duration
        obj.next_maintenance_phase = None
        return obj
    
    def __str__(self) -> str:
        # Liefert den Anzeigenamen der MaintenancePhase zurück
        return self.display_name

    def __repr__(self) -> str:
        # Liefert eine detaillierte Repräsentation der MaintenancePhase für Debugging-Zwecke
        return f"<Phase.{self.name}: {self.display_name}>"

    def set_next_phase(self, next_maintenance_phase: 'MaintenancePhase'):
        # Setzt die nächste Phase, stellt sicher, dass es sich um ein MaintenancePhase-Enum-Mitglied handelt
        if isinstance(next_maintenance_phase, MaintenancePhase):
            self.next_maintenance_phase = next_maintenance_phase
        else:
            raise ValueError("next_phase muss ein Mitglied der MaintenancePhase-Enum sein.")     
        
    def next(self) -> 'MaintenancePhase':
        # Gibt die nächste MaintenancePhase zurück
        return self.next_maintenance_phase
                                