class SimulationTopic:

    def __init__(self, description: str, parameters: dict):
        self.description = description
        self.parameters = parameters
        self.isProcessed = False

    def __init__(
        self,
        description: str,
        parameters: dict,
        answer: str,
        overall_ethic_value: float,
        decision: str,
        domain_ethic_values,
        summary_reason: str,
    ):
        self.description = description
        self.parameters = parameters
        self.answer = answer
        self.overall_ethic_value = overall_ethic_value
        self.decision = decision
        self.domain_ethic_values = domain_ethic_values
        self.summary_reason = summary_reason
        self.isProcessed = True

    def __str__(self):
        return f"Beschreibung: {self.description}\nParameter: {self.parameters}\nAntwort: {self.answer}\nEthikskala: {self.overall_ethic_value:.2f}\nEntscheidung: {self.decision}\nGründe: {self.summary_reason}"

    def __repr__(self):
        return f"SimulationTopic({self.description}, {self.parameters}, {self.answer}, {self.overall_ethic_value}, {self.decision}, {self.domain_ethic_values}, {self.summary_reason})"

    def __eq__(self, other):
        return (
            self.description == other.description
            and self.parameters == other.parameters
        )

    def __hash__(self):
        return hash((self.description, self.parameters))

    def process(
        self,
        answer: str,
        overall_ethic_value: float,
        decision: str,
        domain_ethic_values,
        summary_reason: str,
    ):
        self.answer = answer
        self.overall_ethic_value = overall_ethic_value
        self.decision = decision
        self.domain_ethic_values = domain_ethic_values
        self.summary_reason = summary_reason
        self.isProcessed = True
