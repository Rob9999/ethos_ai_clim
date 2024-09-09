from datetime import datetime
from ethos_ai.tool.tool_manager import ToolManager
from ethos_ai.topic.aspiration_topic import AspirationTopic
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.security.security_level import SecurityLevel
from ethos_ai.security.exception.security_access_exception import (
    SecurityAccessException,
)


class ToDoTopic(AspirationTopic):

    def promote_to_todo(topic: AspirationTopic):
        if not topic.isRefined:
            print(
                "Die Aspiration wurde noch nicht verfeinert. Bitte vor der Umsetzung verfeinern."
            )
            return ToDoTopic(
                "Prüfe Deinen Code",
                {},
                "Code überprüfen und Fehler beheben.",
                5.0,
                "GO",
                [5.0, 5.0, 5.0],
                "Fehler können zu unerwartetem Verhalten führen.",
                "Fehlerfreier Code schreiben.",
            )

        todo_topic = ToDoTopic(topic)
        return todo_topic

    def __init__(
        self,
        description,
        parameters,
        answer,
        overall_ethic_value,
        decision,
        domain_ethic_values,
        summary_reason,
        aspiration,
    ):
        super().__init__(
            description,
            parameters,
            answer,
            overall_ethic_value,
            decision,
            domain_ethic_values,
            summary_reason,
            aspiration,
        )
        self.isReadyForIST = (
            True  # Indikator, dass das ToDoTopic bereit ist, im IST umgesetzt zu werden
        )
        self.released_from_secured_identity_card = (
            None  # Sicherheitsstufen-Inhaber, z.B. ein EthosAIIndividual
        )
        self.released_date_time = None  # Zeitpunkt der Freigabe
        self.is_denied = False
        self.advice = None
        self.security_level = SecurityLevel.LOW  # Standard-Sicherheitsstufe

    def __init__(self, aspiration_topic: AspirationTopic):
        super().__init__(aspiration_topic, aspiration_topic.aspiration)
        self.isReadyForIST = True
        self.is_denied = False
        self.advice = None
        self.security_level = SecurityLevel.LOW  # Standard-Sicherheitsstufe
        self.secured_identity_card = (
            None  # Sicherheitsstufen-Inhaber, z.B. ein EthosAIIndividual
        )

    def execution_denied_by_advisor(self, advice):
        self.is_denied = True
        print(f"Die Ausführung des ToDoTopics wurde verweigert: {advice}")
        self.advice = advice

    def get_instructions(self):
        instructions = f"Umsetzung des ToDoTopic:\n"
        instructions += f"Ziel: {self.aspiration}\n"
        instructions += f"Beschreibung: {self.description}\n"
        instructions += f"Parameter: {self.parameters}\n"
        instructions += f"Empfohlene Schritte:\n"
        instructions += f"1. {self.answer} - Dies sollte unter Berücksichtigung der folgenden ethischen Überlegungen durchgeführt werden:\n"
        instructions += f"   - {self.summary_reason}\n"
        success_chance = self.calculate_success_chance()
        instructions += f"\nErfolgschance: {success_chance:.2f}%\n"
        return instructions

    def calculate_success_chance(self):
        base_chance = 75  # Basiswert der Erfolgschance
        for value in self.domain_ethic_values:
            base_chance += (value - 5) * 2  # Beispielhafte Anpassung
        return max(0, min(100, base_chance))

    # Sign and approve the ToDoTopic for execution
    def release_for_execution(
        self, secured_identity_card: SecuredIdentityCard, input_password: str
    ):
        try:
            if not self.isReadyForIST:
                raise SecurityAccessException(
                    message="Das ToDoTopic ist nicht bereit für die Umsetzung im IST.",
                    subject=None,
                    required_level=self.security_level.name,
                    current_level=secured_identity_card.security_level.name,
                )
            if self.is_denied:
                raise SecurityAccessException(
                    message="Die Ausführung des ToDoTopics wurde verweigert.",
                    subject=None,
                    required_level=self.security_level.name,
                    current_level=secured_identity_card.security_level.name,
                )
            if not secured_identity_card:
                raise SecurityAccessException(
                    message="Kein Sicherheitswächter gesetzt.",
                    subject=None,
                    required_level=self.security_level.name,
                    current_level=secured_identity_card.security_level.name,
                )
            secured_identity_card.check_security(self.security_level, input_password)
            self.isReadyForIST = True
            self.released_from_secured_identity_card = secured_identity_card
            self.released_date_time = datetime.now()
            print(
                f"ToDoTopic '{self.description}' wurde durch '{secured_identity_card.name}' freigegeben."
            )
        except SecurityAccessException as e:
            print(f"Sicherheitsausnahme während der Ausführung: {e}")
            self.isReadyForIST = False
            self.is_denied = True
            self.advice = e.message
            self.released_from_secured_identity_card = None
            self.released_date_time = None
            raise e

    def __str__(self):
        base_str = super().__str__()
        return (
            base_str
            + f"\nZielsetzung: {self.aspiration}\nBereit für IST: {self.isReadyForIST}\nSicherheitsstufe: {self.security_level.name}\n"
            + (
                f"Sicherheitswächter: {self.secured_identity_card.name}"
                if self.secured_identity_card
                else "Kein Sicherheitswächter gesetzt."
            )
        )

    def __repr__(self):
        return f"ToDoTopic({self.description}, {self.parameters}, {self.answer}, {self.overall_ethic_value}, {self.decision}, {self.domain_ethic_values}, {self.summary_reason}, {self.aspiration})"
