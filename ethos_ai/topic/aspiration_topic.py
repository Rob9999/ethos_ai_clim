from ethos_ai.simulation.simulation_topic import SimulationTopic
from ethos_ai.util.translate import Translations


class AspirationTopic(SimulationTopic):

    @staticmethod
    def promote_to_aspiration(topic: SimulationTopic):
        aspiration_topic = AspirationTopic(topic)
        return aspiration_topic

    def __init__(
        self,
        description,
        parameters,
        answer,
        overall_ethic_value,
        decision,
        domain_ethic_values,
        summary_reason,
        aspiration=None,
    ):
        super().__init__(
            description,
            parameters,
            answer,
            overall_ethic_value,
            decision,
            domain_ethic_values,
            summary_reason,
        )
        if aspiration is None:
            self.aspiration = self.generate_aspiration()
        else:
            self.aspiration = aspiration
        self.refine_counter = 0  # Zählt die Anzahl der Verfeinerungen
        self.isRefined = False  # Indikator, ob die Aspiration verfeinert und bereit für die Umsetzung ist

    def __init__(self, simulation_topic: SimulationTopic, aspiration=None):
        super().__init__(
            simulation_topic.description,
            simulation_topic.parameters,
            simulation_topic.answer,
            simulation_topic.overall_ethic_value,
            simulation_topic.decision,
            simulation_topic.domain_ethic_values,
            simulation_topic.summary_reason,
        )
        if aspiration is None:
            self.aspiration = self.generate_aspiration()
        else:
            self.aspiration = aspiration
        self.refine_counter = 0  # Zählt die Anzahl der Verfeinerungen
        self.isRefined = False  # Indikator, ob die Aspiration verfeinert und bereit für die Umsetzung ist

    def generate_aspiration(self):
        if self.decision == "GO":
            # Klare Zielsetzung basierend auf der Beschreibung und der Antwort generieren
            aspiration = Translations.translate(
                "ASPIRATION_GOAL", self.answer, self.description
            )
            aspiration += Translations.translate(
                "ASPIRATION_CONSIDERATION", self.summary_reason
            )
            return aspiration
        else:
            return None

    def refine_aspiration(self, refined_aspiration):
        # Diese Methode ermöglicht es, die Aspiration zu verfeinern und anzupassen
        self.refine_counter += 1
        self.aspiration = refined_aspiration
        self.isRefined = True
        print(f"Die Aspiration wurde verfeinert: {self.aspiration}")

    def __str__(self):
        base_str = super().__str__()
        return (
            base_str
            + f"\nZielsetzung: {self.aspiration}\nVerfeinert: {self.isRefined}\nVerfeinerungen: {self.refine_counter}"
        )

    def __repr__(self):
        return f"AspirationsTopic({self.description}, {self.parameters}, {self.answer}, {self.overall_ethic_value}, {self.decision}, {self.domain_ethic_values}, {self.summary_reason}, {self.aspiration})"
