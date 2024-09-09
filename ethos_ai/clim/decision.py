from enum import Enum, auto
from ethos_ai.util.translate import Translations


# Decision enum
class Decision(Enum):
    STOP = auto()
    EMERGENCY_SURVIVAL = auto()
    EMERGENCY_ESSENTIAL = auto()
    EMERGENCY_RECOMMENDED = auto()
    GO = auto()
    NOGO = auto()
    WAIT = auto()
    ADJUST = auto()
    ESCALATE = auto()
    IMPROVE = auto()

    def __init__(self, *args):
        """
        Initializes the Decision enum instance, setting the translated name as an attribute.
        """
        self._translated_name = None

    @property
    def translated_name(self):
        """
        Returns the translated name of the decision. Translates and caches the result on first access.
        """
        if self._translated_name is None:
            self._translated_name = Translations.translate(self.name)
        return self._translated_name

    @classmethod
    def get_all_decisions(cls):
        """
        Returns a list of all translated decision names.
        """
        return [decision.translated_name for decision in cls]

    @classmethod
    def parse_translated_decision(cls, decision_name: str):
        """
        Returns the Decision instance with the specified translated name.
        """
        for decision in cls:
            if decision.translated_name == decision_name:
                return decision
        return None

    @classmethod
    def parse_for_decision(cls, layer_name: str, text: str) -> dict[str, str]:
        """
        Parses the given text to find a translated decision and maps it to the specified layer name.
        Returns None if no decision is found.

        :param layer_name: The name of the layer to which the decision should be mapped.
        :param text: The text to parse for a decision.
        :return: A dictionary mapping the layer name to the found decision, or None if no decision is found.
        """
        decision_dict = {}
        text_lower = text.lower() if text else ""

        # Iterate through all decisions and check if any are in the text
        for decision in cls:
            if decision.translated_name.lower() in text_lower:
                decision_dict[layer_name] = decision.translated_name
                return decision_dict

        # Return None if no decision is found
        return None

    def __str__(self):
        return self.name
