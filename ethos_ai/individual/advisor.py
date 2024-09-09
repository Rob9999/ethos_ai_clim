from ethos_ai.clim.clim_interface import CLIMInterface
from ethos_ai.individual.base_individual import BaseIndividual
from ethos_ai.instruction.instruction import Instruction
from ethos_ai.security.exception.security_access_exception import (
    SecurityAccessException,
)
from ethos_ai.tool.tool_manager import ToolManager
from ethos_ai.topic.to_do_topic import ToDoTopic
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.security.security_level import SecurityLevel


class Advisor(BaseIndividual):
    def __init__(
        self,
        clim: CLIMInterface,
        tool_manager: ToolManager,
        identity_card: SecuredIdentityCard,
    ):
        super().__init__(secured_identity_card=identity_card)
        self.clim = clim  # CLIM-Instanz, die dem Advisor zur Verfügung steht
        self.tool_manager = (
            tool_manager  # ToolManager-Instanz, die dem Advisor zur Verfügung steht
        )
        self.active_todos: list[ToDoTopic] = []  # Liste der aktiven ToDoTopics

    # Add a ToDoTopic
    def add_todo(self, todo_topic: ToDoTopic):
        if isinstance(todo_topic, ToDoTopic):
            self.active_todos.append(todo_topic)
            print(f"ToDoTopic hinzugefügt: {todo_topic.description}")
            return True
        else:
            print("Ungültiges ToDoTopic.")
            return False

    # Add multiple ToDoTopics
    def add_todos(self, todo_topics: list[ToDoTopic]):
        return [self.add_todo(todo) for todo in todo_topics]

    # Consult the CLIM for advice
    def consult_clim(self, todo_topic: ToDoTopic):
        # Der Advisor fragt das CLIM um Rat, bevor eine Aktion im IST ausgeführt wird
        advice = self.clim.generate_text(
            f"Bitte berate mich (min. GO or NO GO plus Beratung) zur Durchführung der Aufgabe:\n{todo_topic.get_instructions()}.\nZiel: {todo_topic.aspiration}"
        )
        print(f"Beratung durch CLIM: {advice}")
        return advice

    def evaluate_todo_topic(self, todo_topic: ToDoTopic):
        # Der Advisor fragt das CLIM um Rat, bevor eine Aktion im IST ausgeführt wird
        advice = self.consult_clim(todo_topic)
        # Entscheidung auf Basis der Beratung
        if "GO" in advice:
            if self.approve_todo_for_execution(
                todo_topic, self.secured_identity_card.password
            ):
                print(
                    f"ToDoTopic erfolgreich freigegebn zur Ausführung im IST: {todo_topic.description}"
                )
                return True
            else:
                print(
                    f"ToDoTopic '{todo_topic.description}' konnte nicht freigegeben werden."
                )
                self.decline_todo_topic(todo_topic, advice)
                return False
        else:
            print(
                f"Beratung deutet auf NO GO hin. ToDoTopic wird nicht ausgeführt: {todo_topic.description}"
            )
            self.decline_todo_topic(todo_topic, advice)
            return False

    def decline_todo_topic(self, todo_topic: ToDoTopic, advice):
        todo_topic.isReadyForIST = False
        todo_topic.isRefined = False
        todo_topic.execution_denied_by_advisor(advice)

    # Sign and approve the ToDoTopic for execution
    def approve_todo_for_execution(self, todo_topic: ToDoTopic, input_password):
        try:
            # Sicherheitsüberprüfung durch den Advisor
            self.secured_identity_card.check_security(
                SecurityLevel.MEDIUM, input_password
            )
            # Unterschrift des Advisors
            todo_topic.release_for_execution(self.secured_identity_card, input_password)
            print(
                f"ToDoTopic '{todo_topic.description}' wurde durch Advisor '{self.identity_card.name}' zur Ausführung freigegeben."
            )
            return True
        except SecurityAccessException as e:
            print(f"Freigabe fehlgeschlagen: {e}")
            return False

    # Execute the ToDoTopics, if it fails, return the ToDoTopic
    def pop_and_execute_todo(self) -> tuple[ToDoTopic, str]:
        if not self.active_todos:
            print("Keine aktiven ToDoTopics vorhanden.")
            return None, "Keine aktiven ToDoTopics."
        todo_topic = self.active_todos.pop(0)
        return self.execute_todo(todo_topic)

    # Execute the ToDoTopic, if it fails, return the ToDoTopic
    def execute_todo(self, todo_topic: ToDoTopic) -> tuple[ToDoTopic, str]:
        if not isinstance(todo_topic, ToDoTopic):
            print("Kein ToDoTopic vorhanden.")
            return None, "Kein ToDoTopic vorhanden."
        print(f"Starte Ausführung des ToDoTopic: {todo_topic.description}")
        if not self.evaluate_todo_topic(todo_topic):
            return todo_topic, "ToDoTopic nicht freigegeben."
        # generate instruction from ToDoTopic
        instruction = Instruction.promote_to_instruction(
            clim=self.clim,
            tool_manager=self.tool_manager,
            todo_topic=todo_topic,
            secured_id_card=self.secured_identity_card,
        )
        if instruction is None:
            return todo_topic, "Instruction konnte nicht erstellt werden."
        # execute instruction
        instruction.execute()
        return None, "ToDoTopic erfolgreich ausgeführt."

    def review_todos(self):
        # Zeigt alle aktiven ToDoTopics an
        if not self.active_todos:
            print("Keine aktiven ToDoTopics vorhanden.")
        else:
            print("Aktive ToDoTopics:")
            for todo in self.active_todos:
                print(f"- {todo.description}: {todo.aspiration}")

    def __str__(self):
        return f"Advisor {self.get_name()} mit {len(self.active_todos)} aktiven ToDoTopics."

    def __repr__(self):
        return self.__str__()
