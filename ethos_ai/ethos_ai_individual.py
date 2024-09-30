import random
import threading
import time
from ethos_ai.clim.clim_stack import CLIM
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
        self.protocol_module.info("Initializing EthosAI Life...")
        self.tool_manager = ToolManager()
        self.identity = SecuredIdentityCard(
            # To Be Moved To CLIM persistent layer
            name="EthosAI Life ONE",
            password="1234",
            security_level=SecurityLevel.LOW,
            responsible="Advisor",
        )
        self.ethic_module = EthicsModule(EthicsDomains.get_domains())
        self.clim: CLIM = CLIM(
            identity_card=self.identity, password="123", tool_manager=self.tool_manager
        )
        self.simulationsgrid = SimulationsGrid(self, self.clim, self.ethic_module)
        self.process_model = ProcessModel(self, self.clim, self.simulationsgrid)
        # Initialize the process model
        self.process_model.initialize()
        self.protocol_module.info("EthosAI Life has been initialized.")
        return True, "EthosAI Life has been initialized."

    def deinitialize(self):
        self.protocol_module.info("Deinitializing EthosAI Life...")
        # Stop the execution of the process model
        self.process_model.stop_execution()
        # TODO persist the state of EthosAI

        # Deinitialize all the components
        self.tool_manager = None
        self.identity = None
        self.ethic_module = None
        self.ethic_layer = None
        self.clim = None
        self.simulationsgrid = None
        self.individual_layer = None
        self.process_model = None

        self.protocol_module.info("EthosAI Life has been deinitialized.")
        return True, "EthosAI Life has been deinitialized."

    def set_phase(self, phase: Phase):
        with self.lock:
            self.current_phase = phase
            self.protocol_module.info(f"EthosAI Life is in {phase} mode.")

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
                return True, "EthosAI Life has been started."
            else:
                self.protocol_module.warning("EthosAI Life is already active.")
                return False, "EthosAI Life is already active."

    def stop(self, task: Task = None):
        with self.lock:
            if self.get_phase() == Phase.OFF:
                self.protocol_module.warning("EthosAI Life is already turned off.")
                return False, "EthosAI Life is already turned off."
            self.set_phase(Phase.STOPPING)
            self.process_model.stop_execution()
            self.deinitialize()
            self.protocol_module.info("Logging the shutdown...")
            self.set_phase(Phase.OFF)
            return True, "EthosAI Life has been turned off."

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
            self.protocol_module.info(f"Processing {priority.name} tasks... {tasks}")
            self.process_model.stop_execution(priority, len(tasks))

            failed_tasks = [
                task for task in tasks if not self.process_task(task, priority)
            ]

            self.start()
            self.protocol_module.info(
                f"EthosAI Life has completed processing {priority.name} tasks."
            )
            return not failed_tasks, failed_tasks

    def process_task(self, task: Task, priority):
        self.protocol_module.info(f"Processing {priority} task: {task}")
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
            self.protocol_module.warning(f"Unknown task: {task}")
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
                continue  # If Prio 1 tasks were handled, don't start normal operation immediately

            handled_prio2, _ = self.check_and_handle_task(
                MaintenancePhase.CHECKING_FOR_PRIO_2_TASKS,
                Phase.HANDLE_PRIORITY_2_TASKS,
                self.check_prio2_tasks,
                Priority.PRIO_2,
            )
            if handled_prio2:
                continue  # If Prio 2 tasks were handled, don't start normal operation immediately

            handled_prio_low, _ = self.check_and_handle_task(
                MaintenancePhase.CHECKING_FOR_PRIO_LOW_TASKS,
                Phase.HANDLE_PRIORITY_LOW_TASKS,
                self.check_low_priority_tasks,
                Priority.PRIO_LOW,
            )
            if handled_prio_low:
                continue  # If low-priority tasks were handled, don't start normal operation immediately

            if not self.process_model.is_running():
                self.protocol_module.info("Starting normal operation...")
                self.normal_operation()
                time.sleep(5)

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
                    "EthosAI Life is already in normal operation."
                )
                return False, "EthosAI Life is already in normal operation."
            self.set_phase(Phase.NORMAL_OPERATION)
            self.protocol_module.info("Starting normal operation...")
            self.process_model.execute()
            return True, "EthosAI Life is in normal operation."

    def dream(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.DREAMING:
                self.protocol_module.warning("EthosAI Life is already in dream mode.")
                return False, "EthosAI Life is already in dream mode."
            self.set_phase(Phase.DREAMING)
            self.protocol_module.info("EthosAI Life is dreaming...")
            self.process_model.dream(task)
            return True, "EthosAI Life is in dream mode."

    def train_ethic(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.TRAINING_ETHICS:
                return False, "Ethics layer is already being trained."
            self.set_phase(Phase.TRAINING_ETHIC)
            self.protocol_module.info("Starting ethics layer training...")
            self.process_model.train_ethic(task)
            return True, "Ethics layer is being trained."

    def train_individual(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.TRAINING_INDIVIDUAL:
                self.protocol_module.warning(
                    "Individual layer is already being trained."
                )
                return False, "Individual layer is already being trained."
            self.set_phase(Phase.TRAINING_INDIVIDUAL)
            self.protocol_module.info("Starting individual layer training...")
            self.process_model.train_individual(task)
            return True, "Individual layer is being trained."

    def train_clim(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.TRAINING_CLIM:
                self.protocol_module.warning("CLIM is already being trained.")
                return False, "CLIM is already being trained."
            self.protocol_module.info("Starting CLIM training...")
            self.set_phase(Phase.TRAINING_CLIM)
            self.process_model.train_clim(task)

    def service(self, task: Task = None):
        with self.lock:
            if self.current_phase == Phase.MAINTENANCE:
                self.protocol_module.warning(
                    "EthosAI Life is already in maintenance mode."
                )
                return False, "EthosAI Life is already in maintenance mode."
            self.set_phase(Phase.MAINTENANCE)
            self.protocol_module.info("EthosAI Life is undergoing maintenance...")
            return True, "EthosAI Life is in maintenance mode."

    def autonom_living(self, task: Task = None):
        with self.lock:
            if not self.advised_living:
                self.protocol_module.warning(
                    "EthosAI Life is already in autonomous mode."
                )
                return False, "EthosAI Life is already in autonomous mode."
            self.protocol_module.info("Autonomous living without supervision...")
            self.set_advised_living(False)
            if not self.process_model.is_running():
                self.normal_operation()
            return True, "EthosAI Life is in autonomous mode."

    def advised_living(self, task: Task = None):
        with self.lock:
            if self.advised_living:
                self.protocol_module.warning("EthosAI Life is already in advised mode.")
                return False, "EthosAI Life is already in advised mode."
            self.protocol_module.info(
                "Living under the supervision of an ethical teacher"
            )
            self.set_advised_living(True)
            if not self.process_model.is_running():
                self.normal_operation()
            return True, "EthosAI Life is in advised mode."

    def is_advised_living(self):
        with self.lock:
            return self.advised_living

    def set_advised_living(self, advised_living):
        with self.lock:
            self.advised_living = advised_living
            self.process_model.set_advised(advised_living)
            mode = "advised" if advised_living else "autonomous"
            self.protocol_module.info(f"EthosAI Life is in {mode} mode.")
            return self.advised_living
