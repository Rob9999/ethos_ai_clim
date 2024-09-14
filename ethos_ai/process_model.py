import threading
import time

from ethos_ai.clim.clim_interface import CLIMInterface
from ethos_ai.clim.train_list_generator import TrainListGenerator
from ethos_ai.clim.training_status import TrainingStatus
from ethos_ai.ethic.ethics import Ethics
from ethos_ai.state.phase import Phase
from ethos_ai.state.process_phase import ProcessPhase, ProcessPhaseDetails
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
        self._life_imagination = life_imagination
        self.simulation_grid = simulation_grid
        self._execution_thread = None
        self._stop_event = threading.Event()
        self._current_phase: ProcessPhaseDetails = ProcessPhaseDetails(ProcessPhase.OFF)
        self._lock = threading.RLock()
        self.advised = False
        self.task_queue = []
        self.aspirations = []
        self.long_term_aspirations = []
        self.todos = []
        self.ethics = Ethics("ethics.json")

    def initialize(self):
        self.protocol.info("Initializing process model...")

    def _evaluate_tasks(self):
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
    def _ethical_evaluation(self):
        with self._lock:
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
    def _simulate_solutions(self):
        with self._lock:
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

    def _implement_solution(self):
        with self._lock:
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
                self.todos = self._life_imagination.execute_advised(self.todos)
            else:
                self.todos = self._life_imagination.execute_unadvised(self.todos)
            return True, "Solution implemented."

    def _integrate_learning(self):
        self.protocol.info("Integrating experiences into the life imagination...")

        # Step 1: Load test cases and start training
        train_data = TrainListGenerator.load_test_cases_from_directory("test_data")
        self._life_imagination.start_training_async(train_data)

        status_all = None
        while (status_all := self._life_imagination.get_training_status()) and not all(
            status
            in [TrainingStatus.NONE, TrainingStatus.STOPPED, TrainingStatus.FAILED]
            for status in status_all.values()
        ):
            time.sleep(10)
            self.protocol.info(f"Training status: {status_all}")

        # Step 2: Persist the model(s)
        # self._life_imagination.persist_model()

        # Step 3: Restart the CLIM
        # self.life_imagination.restart()

        # Step 4: Test the trained layers on the test cases
        self.protocol.info("Training completed.")

        # Store the test results for each layer and compare with expected results
        test_results = {}

        for layer_name, data in train_data.items():
            test_results[layer_name] = []
            for request in data:
                scenario = TrainListGenerator.get_scenario_description(request)
                expected_decision = TrainListGenerator.get_decision(request)
                type = (
                    "prerun" if layer_name in ["ETHIC", "INDIVIDUAL", "SAMT"] else "all"
                )
                layer_result = self.layer_request(type, layer_name, scenario)
                layer_response = layer_result.get("response")
                layer_decision = layer_result.get("decision")
                layer_score = self.evaluate_clim_output(
                    layer_decision, expected_decision
                )
                # success, decision, summary = self.single_request(request=scenario)
                # clim_score = self.evaluate_clim_output(decision, expected_decision)
                test_results[layer_name].append((scenario, layer_score))
                self.protocol.info(
                    f"Test result for {layer_name}: {scenario}, Layer Score: {layer_score}, Layer Response: {layer_response}, Layer Decision: {layer_decision}, Expected Decision: {expected_decision}"
                )

        # Step 5: Analyze the results and provide feedback
        total_score = sum(
            [score for layer in test_results.values() for _, score in layer]
        )
        self.protocol.info(f"Overall CLIM performance score: {total_score}")
        return test_results

    def evaluate_clim_output(self, output, expected_decision):
        """
        Compare the CLIM output with the expected decision and return a score.
        Scoring can be customized based on different criteria.
        """
        if output == expected_decision:
            return 1  # Correct decision
        else:
            return 0  # Incorrect decision

    def _check_deviations(self):
        self.protocol.info("Checking deviations...")
        time.sleep(1)  # Simulate time taken for the task

    def dream(self, task: Task = None):
        with self._lock:
            self.protocol.info("Dreaming...")
            self.protocol.info("Task: {}".format(task))
            time.sleep(1)  # Simulate time taken for the task
            self.protocol.info("Dreaming completed.")

    def train_ethic(self, task: Task = None):
        with self._lock:
            self.protocol.info("Starte das Training der Ethikschicht...")
            self.protocol.info("Task: {}".format(task))
            time.sleep(1)  # Simulate time taken for the task
            self.protocol.info("Training der Ethikschicht abgeschlossen.")

    def train_individual(self, task: Task = None):
        with self._lock:
            self.protocol.info("Starte das Training der Individualschicht...")
            self.protocol.info("Task: {}".format(task))
            time.sleep(1)  # Simulate time taken for the task
            self.protocol.info("Training der Individualschicht abgeschlossen.")

    def train_clim(self, task: Task = None):
        with self._lock:
            self.protocol.info("Starte das Training der CLIM...")
            self.protocol.info("Task: {}".format(task))
            time.sleep(1)
            self.protocol.info("Training der CLIM abgeschlossen.")

    def layer_request(self, type: str, layer: str, request: str) -> dict[str, str]:
        self.protocol.info(Translations.translate("REQUEST", request))
        return self.simulation_grid.run_simulation_on_layer(type, layer, request)

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
        with self._lock:
            return self._current_phase.get_phase() == ProcessPhase.RUNNING

    def shall_stop(self):
        return self._stop_event.is_set()

    def set_advised(self, advised):
        with self._lock:
            self.advised = advised

    def submit_task(self, task):
        with self._lock:
            self.task_queue.append(task)

    def _run(self):
        """Main loop of the process model."""
        if not self.shall_stop():
            self._life_imagination.start()
        while not self.shall_stop():
            # if not self.shall_stop():
            #    self._evaluate_tasks()
            # if not self.shall_stop():
            #    self._ethical_evaluation()
            # if not self.shall_stop():
            #    self._simulate_solutions()
            # if not self.shall_stop():
            #    self._implement_solution()
            if not self.shall_stop():
                self._integrate_learning()
            if not self.shall_stop():
                self._check_deviations()
        self._life_imagination.stop()

    def execute(self, advised=False):
        with self._lock:
            self.protocol.info(f"Process model should start (advised: {advised})...")
            if self._current_phase.get_phase() == ProcessPhase.OFF:
                self._stop_event.clear()
            else:
                self.protocol.info("Process model is already active.")
                return False, "Process model is already active."

            self._execution_thread = threading.Thread(target=self._run)
            self._current_phase.set_phase(ProcessPhase.RUNNING)
            self._execution_thread.start()
            time.sleep(4)
            self.protocol.info("Process model started.")
            return True, "Process model started."

    def stop_execution(
        self, priority: "Priority" = Priority.NORMAL, task_count: int = 0
    ):
        with self._lock:
            self.protocol.info(
                f"Process model should stop (priority: {priority}, tasks: {task_count})..."
            )
            if self._current_phase.get_phase() == ProcessPhase.OFF:
                self.protocol.info("Process model is already inactive.")
                return False, "Process model is already inactive."
            self._stop_event.set()
        self._execution_thread.join()
        with self._lock:
            report = self._current_phase.complete_phase(
                "Success", "Process model and CLIM stopped completly."
            )
            self._current_phase.set_phase(ProcessPhase.OFF)
            self._execution_thread = None
            self.protocol.info(f"Process model stopped. Running Phase Report: {report}")
            return True, "Process model stopped."
