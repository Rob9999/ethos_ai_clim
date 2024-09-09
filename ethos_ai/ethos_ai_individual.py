import random
import threading
from ethos_ai.clim.clim import CLIM
from ethos_ai.security.securied_identity_card import SecurityLevel, SecuredIdentityCard
from ethos_ai.task.task import Task
from ethos_ai.task.task_type import TaskType
from ethos_ai.state.maintenance_phase import MaintenancePhase
from ethos_ai.state.phase import Phase
from ethos_ai.state.priority import Priority
from ethos_ai.tool.tool_manager import ToolManager
from ethos_ai.util.protocol import Protocol
from ethos_ai.process_model import ProcessModel
from ethos_ai.ethic.ethics_domains import EthicsDomains
from ethos_ai.ethic.ethics_module import EthicsModule
from ethos_ai.simulation.simulation_grid import SimulationsGrid
from enum import Enum


class EthosAIIndividual:
    def __init__(self):
        self.protocol_module = Protocol("WARNING")
        self.current_phase: Phase = Phase.OFF
        self.maintenance_phase: MaintenancePhase = MaintenancePhase.NONE
        self.execution_thread = None
        self._stop_event = threading.Event()
        self.lock = threading.RLock()
        self.advised_living = False

    def initialize(self):
        self.protocol_module.info("EthosAI Life wird initialisiert...")
        self.tool_manager = ToolManager()
        self.identity = SecuredIdentityCard(
            # To Be Moved To CLIM persistant layer
            name="EthosAI Life ONE",
            password="1234",
            security_level=SecurityLevel.LOW,
            responsible="Advisor",
        )
        self.ethic_module = EthicsModule(EthicsDomains.get_domains())
        self.clim: CLIM = CLIM(
            identity_card=self.identity, password="123", tool_manager=self.tool_manager
        )
        self.clim.set_generation_parameters(max_length=256, max_new_tokens=100)
        self.simulationsgrid = SimulationsGrid(self, self.clim, self.ethic_module)
        self.process_model = ProcessModel(self, self.clim, self.simulationsgrid)
        # Initialize the process model
        self.process_model.initialize()
        self.protocol_module.info("EthosAI Life wurde initialisiert.")
        return True, "EthosAI Life wurde initialisiert."

    def deinitialize(self):
        self.protocol_module.info("EthosAI Life wird deinitialisiert...")
        # Stop the execution of the process model
        self.process_model.stop_execution()
        # TODO persist the state of the EthosAI

        # Deinitialize all the components
        self.tool_manager = None
        self.identity = None
        self.ethic_module = None
        self.ethic_layer = None
        self.clim = None
        self.simulationsgrid = None
        self.individual_layer = None
        self.process_model = None

        self.protocol_module.info("EthosAI Life wurde deinitialisiert.")
        return True, "EthosAI Life wurde deinitialisiert."

    def set_phase(self, phase: Phase):
        with self.lock:
            self.current_phase = phase
            self.protocol_module.info(f"EthosAI Life ist im {phase}-Modus.")

    def get_phase(self) -> Phase:
        with self.lock:
            return self.current_phase

    def start(self, task: Task = None):
        with self.lock:
            if self.get_phase() == Phase.OFF:
                self._stop_event.clear()
                self.set_phase(Phase.STARTING)
                self.initialize()
                self.execution_thread = threading.Thread(target=self.run)
                self.execution_thread.start()
                return True, "EthosAI Life wurde gestartet."
            else:
                self.protocol_module.warning("EthosAI Life ist bereits aktiv.")
                return False, "EthosAI Life ist bereits aktiv."

    def stop(self, task: Task = None):
        with self.lock:
            if self.get_phase() == Phase.OFF:
                self.protocol_module.warning("EthosAI Life ist bereits ausgeschaltet.")
                return False, "EthosAI Life ist bereits ausgeschaltet."
            self.set_phase(Phase.STOPPING)
            self.process_model.stop_execution()
            self.deinitialize()
            self.protocol_module.info("Protokollierung des Shutdowns...")
            self.set_phase(Phase.OFF)
            return True, "EthosAI Life wurde ausgeschaltet."

    def check_tasks(self, phase: MaintenancePhase, task_check_function):
        with self.lock:
            self.set_phase(Phase.MAINTENANCE)
            self.maintenance_phase = phase
            tasks = task_check_function()
            self.maintenance_phase = MaintenancePhase.NONE
            return tasks

    def handle_tasks(self, phase: Phase, tasks: list, priority: Priority):
        with self.lock:
            self.set_phase(phase)
            self.protocol_module.info(
                f"Bearbeitung der {priority.name} Aufgaben... {tasks}"
            )
            self.process_model.stop_execution(priority, len(tasks))

            failed_tasks = [
                task for task in tasks if not self.process_task(task, priority)
            ]

            self.start()
            self.protocol_module.info(
                f"EthosAI Life hat die Bearbeitung der {priority.name} Aufgaben abgeschlossen."
            )
            return not failed_tasks, failed_tasks

    def process_task(self, task: Task, priority):
        self.protocol_module.info(f"Bearbeitung der {priority} Aufgabe: {task}")
        task_type = task.get_type()

        task_function_mapping = {
            TaskType.SERVICE: self.service,
            TaskType.DREAM: self.dream,
            TaskType.TRAIN_ETHIC: self.train_ethic,
            TaskType.TRAIN_INDIVIDUAL: self.train_individual,
            TaskType.TRAIN_CLIM: self.train_clim,
            TaskType.STOP: self.stop,
            TaskType.START: self.start,
            TaskType.AUTONOM_LIVING: self.autonom_living,
            TaskType.ADVISED_LIVING: self.advised_living,
        }

        if task_type in task_function_mapping:
            task_function_mapping[task_type](task)
            return True
        else:
            self.protocol_module.warning(f"Unbekannte Aufgabe: {task}")
            return False

    # check and handle task if any according to the specified parameters
    def check_and_handle_task(
        self,
        maintenance_phase: MaintenancePhase,
        phase: Phase,
        task_check_function,
        priority: Priority,
    ):
        with self.lock:
            if not self._stop_event.is_set():
                tasks = self.check_tasks(maintenance_phase, task_check_function)
                if tasks:
                    return self.handle_tasks(phase, tasks, priority)
                return False, []

    # main loop of the EthosAI
    def run(self):
        while not self._stop_event.is_set():
            handled_prio1, _ = self.check_and_handle_task(
                MaintenancePhase.CHECKING_FOR_PRIO_1_TASKS,
                Phase.HANDLE_PRIORITY_1_TASKS,
                self.check_prio1_tasks,
                Priority.PRIO_1,
            )
            if handled_prio1:
                continue  # Wenn Prio 1 Aufgaben behandelt wurden, starte den normalen Betrieb nicht sofort

            handled_prio2, _ = self.check_and_handle_task(
                MaintenancePhase.CHECKING_FOR_PRIO_2_TASKS,
                Phase.HANDLE_PRIORITY_2_TASKS,
                self.check_prio2_tasks,
                Priority.PRIO_2,
            )
            if handled_prio2:
                continue  # Wenn Prio 2 Aufgaben behandelt wurden, starte den normalen Betrieb nicht sofort

            handled_prio_low, _ = self.check_and_handle_task(
                MaintenancePhase.CHECKING_FOR_PRIO_LOW_TASKS,
                Phase.HANDLE_PRIORITY_LOW_TASKS,
                self.check_low_priority_tasks,
                Priority.PRIO_LOW,
            )
            if handled_prio_low:
                continue  # Wenn niedrige Prioritätsaufgaben behandelt wurden, starte den normalen Betrieb nicht sofort

            self.protocol_module.info("Start des normalen Betriebs...")
            self.normal_operation()

    def check_prio1_tasks(self):
        # Implement logic to check for Prio 1 tasks
        return []

    def check_prio2_tasks(self):
        # Implement logic to check for Prio 2 tasks
        return []

    def check_low_priority_tasks(self):
        # Implement logic to check for low priority tasks
        if random.randint(1, 10) == 1:
            return [Task(TaskType.DREAM)]
        return []

    def submit_normal_operation_task(self, task):
        with self.lock:
            self.process_model.submit_task(task)

    def normal_operation(self, task: Task = None):
        with self.lock:
            if self.process_model.is_running():
                self.protocol_module.warning(
                    "EthosAI Life ist bereits im normalen Betrieb."
                )
                return False, "EthosAI Life ist bereits im normalen Betrieb."
            self.set_phase(Phase.NORMAL_OPERATION)
            self.protocol_module.info("Start des normalen Betriebs...")
            self.process_model.execute()
            return True, "EthosAI Life ist im normalen Betrieb."

    def dream(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.DREAMING:
                self.protocol_module.warning("EthosAI Life ist bereits im Traummodus.")
                return False, "EthosAI Life ist bereits im Traummodus."
            self.set_phase(Phase.DREAMING)
            self.protocol_module.info("EthosAI Life träumt...")
            self.clim.ethic_layer.train()
            return True, "EthosAI Life ist im Traummodus."

    def train_ethic(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.TRAINING_ETHICS:
                return False, "Ethikschicht wird bereits trainiert."
            self.set_phase(Phase.TRAINING_ETHIC)
            self.protocol_module.info("Starte das Training der Ethikschicht...")
            self.clim.ethic_layer.train()
            return True, "Ethikschicht wird trainiert."

    def train_individual(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.TRAINING_INDIVIDUAL:
                self.protocol_module.warning(
                    "Individualschicht wird bereits trainiert."
                )
                return False, "Individualschicht wird bereits trainiert."
            self.set_phase(Phase.TRAINING_INDIVIDUAL)
            self.protocol_module.info("Starte das Training der Individualschicht...")
            self.clim.individual_layer.train()
            return True, "Individualschicht wird trainiert."

    def train_clim(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.TRAINING_CLIM:
                self.protocol_module.warning("CLIM wird bereits trainiert.")
                return False, "CLIM wird bereits trainiert."
            self.protocol_module.info("Starte das Training des CLIM...")
            self.set_phase(Phase.TRAINING_CLIM)
            self.clim.train()

    def service(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.SERVICE:
                self.protocol_module.warning(
                    "EthosAI Life ist bereits im Wartungsmodus."
                )
                return False, "EthosAI Life ist bereits im Wartungsmodus."
            self.set_phase(Phase.SERVICE)
            self.protocol_module.info("EthosAI Life wird gewartet...")
            return True, "EthosAI Life ist im Wartungsmodus."

    def autonom_living(self, task: Task = None):
        with self.lock:
            if not self.advised_living:
                self.protocol_module.warning(
                    "EthosAI Life ist bereits im autonomen Modus."
                )
                return False, "EthosAI Life ist bereits im autonomen Modus."
            self.protocol_module.info("Autonomes Leben ohne Überwachung...")
            self.set_advised_living(False)
            if not self.process_model.is_running():
                self.normal_operation()
            return True, "EthosAI Life ist im autonomen Modus."

    def advised_living(self, task: Task = None):
        with self.lock:
            if self.advised_living:
                self.protocol_module.warning(
                    "EthosAI Life ist bereits im beratenen Modus."
                )
                return False, "EthosAI Life ist bereits im beratenen Modus."
            self.protocol_module.info("Leben unter Überwachung eines ethischen Lehrers")
            self.set_advised_living(True)
            if not self.process_model.is_running():
                self.normal_operation()
            return True, "EthosAI Life ist im beratenen Modus."

    def is_advised_living(self):
        with self.lock:
            return self.advised_living

    def set_advised_living(self, advised_living):
        with self.lock:
            self.advised_living = advised_living
            self.process_model.set_advised(advised_living)
            mode = "beratenen" if advised_living else "autonomen"
            self.protocol_module.info(f"EthosAI Life ist im {mode} Modus.")
            return self.advised_living
