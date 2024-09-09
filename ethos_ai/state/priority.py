from enum import Enum

class Priority(Enum):
    
    EMERGENCY = ("Notfall", "Dringendste Priorität", 1)
    PRIO_1 = ("Priorität 1", "Sehr hohe Priorität", 2)
    PRIO_2 = ("Priorität 2", "Hohe Priorität", 3)
    NORMAL = ("Normal", "Normale Priorität", 4)
    PRIO_LOW = ("Niedrigpriorisiert", "Geringe Priorität", 5)
        
    def __new__(cls, display_name: str, description: str, priority: int):
        obj = object.__new__(cls)
        obj._value_ = priority  # Verwende den Prioritätswert direkt als Enum-Wert
        obj.display_name = display_name
        obj.description = description
        obj.priority = priority
        return obj
    
    def __str__(self) -> str:
        # Liefert den Anzeigenamen der Priorität zurück
        return self.display_name

    def __repr__(self) -> str:
        # Liefert eine detaillierte Repräsentation der Priorität für Debugging-Zwecke
        return f"<Priority.{self.name}: {self.display_name}, priority={self.priority}>"

    # Vergleichsfunktionen basierend auf der Priorität
    def __lt__(self, other):
        if isinstance(other, Priority):
            return self.priority < other.priority
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, Priority):
            return self.priority <= other.priority
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, Priority):
            return self.priority > other.priority
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, Priority):
            return self.priority >= other.priority
        return NotImplemented
