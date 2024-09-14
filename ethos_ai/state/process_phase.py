from enum import Enum
from datetime import datetime
from datetime import timezone


class ProcessPhase(Enum):
    OFF = "Off"
    RUNNING = "Running"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()


class ProcessPhaseDetails:
    def __init__(
        self,
        phase: ProcessPhase,
        phase_id: str = None,
        phase_type: str = "Process",
        phase_status: str = "Off",
        phase_result: str = None,
        phase_message: str = None,
    ):
        self._initialize(
            phase=phase,
            phase_id=phase_id,
            phase_type=phase_type,
            phase_status=phase_status,
            phase_result=phase_result,
            phase_message=phase_message,
        )
        self.start_phase()

    def _initialize(
        self,
        phase: ProcessPhase,
        phase_id: str = None,
        phase_type: str = "Process",
        phase_status: str = "Off",
        phase_result: str = None,
        phase_message: str = None,
    ):
        self._phase = phase if phase is not None else ProcessPhase.OFF
        self._phase_id = phase_id if phase_id is not None else str(self._phase.value)
        self._phase_type = phase_type
        self._phase_status = phase_status
        self._phase_result = phase_result
        self._phase_message = phase_message
        self._phase_start_time = None
        self._phase_end_time = None
        self._phase_duration = None

    def set_phase(
        self,
        phase: ProcessPhase,
        phase_id: str = None,
        phase_type: str = None,
    ):
        """Sets the phase of the process."""
        self._initialize(
            phase=phase,
            phase_id=phase_id if phase_id is not None else self._phase_id,
            phase_type=phase_type if phase_type is not None else self._phase_type,
        )
        self.start_phase()

    def get_phase(self):
        """Returns the phase of the process."""
        return self._phase

    def start_phase(self):
        """Sets the start timestamp when the phase begins."""
        self._phase_start_time = datetime.utcnow()
        self._phase_status = "Running"
        # print(f"Phase {self._phase.value} started at {self._phase_start_time}")

    def complete_phase(self, result: str, message: str = None) -> dict:
        """Completes the phase by setting the end timestamp, result, and optional message."""
        self._phase_end_time = datetime.now(tz=timezone.utc)
        self._phase_duration = self._phase_end_time - self._phase_start_time.replace(
            tzinfo=timezone.utc
        )
        self._phase_status = "Completed"
        self._phase_result = result
        self._phase_message = message
        # print(f"Phase {self._phase.value} completed at {self._phase_end_time}")
        # print(f"Duration: {self._phase_duration}")
        return self.to_string()

    def __str__(self):
        return (
            f"ProcessPhaseDetails(phase={self._phase}, phase_id={self._phase_id}, "
            f"phase_type={self._phase_type}, phase_status={self._phase_status}, "
            f"phase_start_time={self._phase_start_time}, phase_end_time={self._phase_end_time}, "
            f"phase_duration={self._phase_duration}, phase_result={self._phase_result}, "
            f"phase_message={self._phase_message})"
        )

    def __repr__(self):
        return self.__str__()

    def to_string(self):
        return self.__str__()

    def to_dict(self) -> dict:
        """Converts the object to a dictionary."""
        return {
            "phase": self._phase.value,
            "phase_id": self._phase_id,
            "phase_type": self._phase_type,
            "phase_status": self._phase_status,
            "phase_start_time": (
                self._phase_start_time.isoformat() if self._phase_start_time else None
            ),
            "phase_end_time": (
                self._phase_end_time.isoformat() if self._phase_end_time else None
            ),
            "phase_duration": (
                str(self._phase_duration) if self._phase_duration else None
            ),
            "phase_result": self._phase_result,
            "phase_message": self._phase_message,
        }

    @staticmethod
    def from_dict(data: dict):
        """Creates an object from a dictionary."""
        obj = ProcessPhaseDetails(
            phase=ProcessPhase(data["phase"]),
            phase_id=data["phase_id"],
            phase_type=data["phase_type"],
            phase_status=data["phase_status"],
            phase_result=data["phase_result"],
            phase_message=data["phase_message"],
        )
        obj._phase_start_time = (
            datetime.fromisoformat(data["phase_start_time"])
            if data["phase_start_time"]
            else None
        )
        obj._phase_end_time = (
            datetime.fromisoformat(data["phase_end_time"])
            if data["phase_end_time"]
            else None
        )
        obj._phase_duration = data["phase_duration"]
        return obj
