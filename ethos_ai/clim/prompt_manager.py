from ethos_ai.clim.decision import Decision
from ethos_ai.util.translate import Translations


class PromptManager:

    def __init__(self):
        self.decisions = f"[{', '.join(Decision.get_all_decisions())}]"
        self.prompts = {}
        self.load_prompts()  # Cache prompts upon initialization

    def load_prompts(self):
        """Lädt die Prompts und cached sie in einem internen Wörterbuch."""
        keys = [
            "PRERUN_ETHIC",
            "PRERUN_INDIVIDUAL",
            "PRERUN_SAMT",
            "ALL_LTCLIM",
            "FINAL_ETHIC",
            "FINAL_INDIVIDUAL",
            "FINAL_SAMT",
            "EMERGENCY_SURVIVAL_ETHIC",
            "EMERGENCY_SURVIVAL_SAMT",
            "EMERGENCY_ESSENTIAL_ETHIC",
            "EMERGENCY_ESSENTIAL_SAMT",
            "EMERGENCY_ESSENTIAL_INDIVIDUAL",
            "EMERGENCY_RECOMMENDED_SAMT",
            "EMERGENCY_RECOMMENDED_INDIVIDUAL",
            "INTERNAL_ERROR",
        ]

        # Lädt die Prompts von der Translations-Klasse und speichert sie.
        for key in keys:
            self.prompts[key] = Translations.translate(key, "{}", "{}")

    def get_prompt(self, type: str, layer_name: str, input_data):
        prompt_key = f"{type.upper()}_{layer_name.upper()}"
        prompt = self.prompts.get(prompt_key)
        if prompt:
            return prompt.format(input_data, self.decisions)
        return None

    def get_error_prompt(self, reason, input_data):
        prompt = self.prompts.get("INTERNAL_ERROR")
        if prompt:
            return prompt.format(reason, Decision.STOP)
        return "Internal error. Decision: STOP"

    def update_prompt(self, layer_name, new_prompt):
        self.prompts[layer_name] = new_prompt
