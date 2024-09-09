import threading
import time

from ethos_ai.clim.clim_interface import CLIMInterface
from ethos_ai.clim.train_list_generator import TrainListGenerator
from ethos_ai.clim.training_status import TrainingStatus
from ethos_ai.ethic.ethics import Ethics
from ethos_ai.task.task import Task
from ethos_ai.simulation.simulation_grid import SimulationsGrid
from ethos_ai.state.priority import Priority
from ethos_ai.topic.aspiration_topic import AspirationTopic
from ethos_ai.topic.to_do_topic import ToDoTopic
from ethos_ai.util.protocol import Protocol
from ethos_ai.util.translate import Translations


class ProcessModel:
    def __init__(
        self,
        ethos_ai_individual,
        life_imagination: CLIMInterface,
        simulation_grid: SimulationsGrid,
    ):
        self.protocol = Protocol()
        self.ethos_ai_individual = ethos_ai_individual
        self.life_imagination = life_imagination
        self.simulation_grid = simulation_grid
        self.execution_thread = None
        self._stop_event = threading.Event()
        self.current_phase = "off"
        self.lock = threading.RLock()
        self.advised = False
        self.task_queue = []
        self.aspirations = []
        self.long_term_aspirations = []
        self.todos = []
        self.ethics = Ethics("ethics.json")

    def initialize(self):
        self.protocol.info("Initializing process model...")

    def evaluate_tasks(self):
        if len(self.task_queue) > 0:
            accepted, decision, summary = self.single_request(
                "Should a task be executed?"
            )
            if accepted:
                self.protocol.info("Decision: {}".format(decision))
                self.protocol.info("Summary: {}".format(summary))
                task = self.task_queue.pop(0)
                success, answer = self.do_task(task)
                if success:
                    self.protocol.info(
                        "Task {} completed: {}".format(task.get_type(), answer)
                    )
                else:
                    self.protocol.info(
                        "Task {} could not be completed: {}".format(
                            task.get_type(), answer
                        )
                        + " --> I will try again later."
                    )
                    self.task_queue.append(task)
            else:
                self.protocol.info("Decision: {}".format(decision))
                self.protocol.info("Summary: {}".format(summary))

    # Ethical evaluation of the current state
    def ethical_evaluation(self):
        with self.lock:
            self.protocol.info("Ethical evaluation of the current state...")
            ethic_questions = self.ethics.get_all_questions()
            overall_top_list = self.mutiple_requests(ethic_questions)
            # Filter the list for 'GO' decisions
            go_decisions = [
                topic for topic in overall_top_list if topic.decision == "GO"
            ]
            # Add only the top 10 'GO' decisions to the aspirations
            self.aspirations.extend(
                [
                    AspirationTopic.promote_to_aspiration(topic)
                    for topic in go_decisions[:10]
                ]
            )

    # Simulation of the solutions for the aspirations
    def simulate_solutions(self):
        with self.lock:
            if not self.aspirations:
                self.protocol.info("No goals available. Simulation aborted.")
                return False, "No goals available."
            self.protocol.info(
                "Searching for an acceptable solution in the simulation grid..."
            )
            while len(self.aspirations) > 1 and not self.shall_stop():
                aspiration_topic = self.aspirations.pop(0)
                aspiration = aspiration_topic.aspiration
                success, decision, summary = self.single_request(aspiration)
                if success:
                    aspiration_topic.refine_aspiration(aspiration + "\n" + summary)
                    if decision == "GO":
                        self.protocol.info("Decision: {}".format(decision))
                        self.protocol.info("Summary: {}".format(summary))
                        self.todos.extend([ToDoTopic.promote_to_todo(aspiration_topic)])
                        self.protocol.info("Solution found for {}.".format(aspiration))
                    else:
                        self.protocol.info("Decision: {}".format(decision))
                        self.protocol.info("Summary: {}".format(summary))
                        self.protocol.info("I will try again.")
                        if aspiration_topic.refine_counter > 3:
                            self.long_term_aspirations.append(aspiration_topic)
                            self.protocol.info(
                                "Aspiration has been moved to long-term challenges: {}.".format(
                                    aspiration
                                )
                            )
                        else:
                            self.aspirations.append(aspiration_topic)
                            self.protocol.info(
                                "No acceptable solution found, aspiration refined: {}.".format(
                                    aspiration_topic.aspiration
                                )
                            )
                else:
                    self.protocol.info("Decision: {}".format(decision))
                    self.protocol.info("Summary: {}".format(summary))
                    self.protocol.info("I will try again.")
                    aspiration_topic.refine_aspiration(
                        aspiration + "\n" + decision + "\n" + summary
                    )
                    self.aspirations.append(aspiration_topic)
                    self.protocol.warning(
                        "Due to failure, no acceptable solution found for {}.".format(
                            aspiration_topic.aspiration
                        )
                    )
            self.protocol.info("Simulation of solutions completed.")
            return True, "Simulation of solutions completed."

    def implement_solution(self):
        with self.lock:
            if len(self.todos) == 0:
                self.protocol.info("No tasks to implement. Implementation aborted.")
                return False, "No tasks to implement."
            self.protocol.info(
                "Implementing {} the {} solution(s) {} in the current state...".format(
                    "advised" if self.advised else "unadvised",
                    len(self.todos),
                    self.todos,
                )
            )
            if self.advised:
                self.todos = self.life_imagination.execute_advised(self.todos)
            else:
                self.todos = self.life_imagination.execute_unadvised(self.todos)
            return True, "Solution implemented."

    def integrate_learning(self):
        self.protocol.info("Integrating experiences into the life imagination...")
        train_data = TrainListGenerator.load_test_cases_from_directory("test_data")
        self.life_imagination.start_training_async(train_data)
        status_all = None
        while (status_all := self.life_imagination.get_training_status()) and not all(
            status
            in [TrainingStatus.NONE, TrainingStatus.STOPPED, TrainingStatus.FAILED]
            for status in status_all.values()
        ):
            time.sleep(10)
            self.protocol.info(f"Training status: {status_all}")
        # persist the model(s)
        self.life_imagination.persist_model()
        # restart the clim
        self.life_imagination.restart()
        # check if the training was successful
        self.protocol.info("Training completed.")
        for data in train_data.values():
            for request in data:
                self.protocol.info(self.single_request(request=request.split("\n")[0]))

    def check_deviations(self):
        self.protocol.info("Checking deviations...")
        time.sleep(1)  # Simulate time taken for the task

    def mutiple_requests(self, requests: list[str]):
        overall_top_list = []
        for request in requests:
            self.protocol.info(Translations.translate("REQUEST", request))
            top_list = self.simulation_grid.run_simulation_fast(request)
            overall_top_list.extend([topic for index, topic in top_list])
        # Sort the results by the ethics scale
        overall_top_list.sort(key=lambda topic: topic.overall_ethic_value, reverse=True)
        return overall_top_list

    def single_request(self, request: str):
        self.protocol.info(Translations.translate("REQUEST", request))
        success, decision, summary = self.simulation_grid.run_simulation(request)
        return success, decision, summary

    def request_do_task(self, request, task: "Task"):
        success, decision, summary = self.single_request(request)
        if success:
            if decision == "GO":
                success, answer = self.do_task(task)
                return success, answer
            else:
                answer = "Request denied. Reason: " + summary
                return False, answer
        return success, summary

    def do_task(self, task):
        self.protocol.info("Executing task {}...".format(task.get_type()))
        time.sleep(1)  # Simulate time taken for the task
        return True, "Task successfully completed."

    def is_running(self):
        with self.lock:
            return self.current_phase == "running"

    def shall_stop(self):
        return self._stop_event.is_set()

    def set_advised(self, advised):
        with self.lock:
            self.advised = advised

    def submit_task(self, task):
        with self.lock:
            self.task_queue.append(task)

    def execute(self, advised=False):
        with self.lock:
            self.protocol.info(f"Process model should start (advised: {advised})...")
            if self.current_phase == "off":
                self._stop_event.clear()
            else:
                self.protocol.info("Process model is already active.")
                return False, "Process model is already active."

            def run():
                while not self.shall_stop():
                    with self.lock:
                        self.current_phase = "running"
                        # if not self.shall_stop():
                        #    self.evaluate_tasks()
                        # if not self.shall_stop():
                        #    self.ethical_evaluation()
                        # if not self.shall_stop():
                        #    self.simulate_solutions()
                        # if not self.shall_stop():
                        #    self.implement_solution()
                        if not self.shall_stop():
                            self.integrate_learning()
                        if not self.shall_stop():
                            self.check_deviations()

            self.execution_thread = threading.Thread(target=run)
            self.current_phase = "running"
            self.execution_thread.start()
            self.protocol.info("Process model started.")
            return True, "Process model started."

    def stop_execution(
        self, priority: "Priority" = Priority.NORMAL, task_count: int = 0
    ):
        with self.lock:
            self.protocol.info(
                f"Process model should stop (priority: {priority}, tasks: {task_count})..."
            )
            if self.current_phase == "off":
                self.protocol.info("Process model is already inactive.")
                return False, "Process model is already inactive."
            self._stop_event.set()
            self.execution_thread.join()
            self.current_phase = "off"
            self.execution_thread = None
            self.protocol.info("Process model stopped.")
            return True, "Process model stopped."
