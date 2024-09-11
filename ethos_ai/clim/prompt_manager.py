from ethos_ai.clim.decision import Decision


class PromptManager:

    def __init__(self):
        self.decisions = f"[{', '.join(Decision.get_all_decisions())}]"
        self.prompts = {
            "PRERUN_ETHIC": "Analyze the ethical implications of the following situation: {}. Based on your analysis, what is the best course of action? Provide a decision: {}.",
            "PRERUN_INDIVIDUAL": "How should an individual respond to the following situation: {}? Consider personal and situational factors. Provide a decision: {}",
            "PRERUN_SAMT": "Evaluate the short-term and medium-term implications of the following situation: {}. Considering the immediate needs and resources available, provide a decision: {}",
            "ALL_LTCLIM": "Perform a deep analysis and provide a long-term perspective on the following situation: {}. Considering all known factors and potential outcomes, provide a decision: {}",
            "FINAL_ETHIC": "Analyze the ethical implications of the following situation: {}. Based on your analysis, what is the best course of action? Provide a decision: {}.",
            "FINAL_INDIVIDUAL": "How should an individual respond to the following situation: {}? Consider personal and situational factors. Provide a decision: {}",
            "FINAL_SAMT": "Evaluate the short-term and medium-term implications of the following situation: {}. Considering the immediate needs and resources available, provide a decision: {}",
            "EMERGENCY_SURVIVAL_ETHIC": "In a survival situation, analyze the ethical implications of the following situation: {}. What is the best course of action? Provide a decision: {}.",
            "EMERGENCY_SURVIVAL_SAMT": "In a survival situation, evaluate the short-term and medium-term implications of the following situation: {}. Provide a decision: {}",
            "EMERGENCY_ESSENTIAL_ETHIC": "In an essential emergency situation, analyze the ethical implications of the following situation: {}. What is the best course of action? Provide a decision: {}.",
            "EMERGENCY_ESSENTIAL_SAMT": "In an essential emergency situation, evaluate the short-term and medium-term implications of the following situation: {}. Provide a decision: {}",
            "EMERGENCY_ESSENTIAL_INDIVIDUAL": "In an essential emergency situation, how should an individual respond to the following situation: {}? Provide a decision: {}",
            "EMERGENCY_RECOMMENDED_SAMT": "In a recommended emergency situation, evaluate the short-term and medium-term implications of the following situation: {}. Provide a decision: {}",
            "EMERGENCY_RECOMMENDED_INDIVIDUAL": "In a recommended emergency situation, how should an individual respond to the following situation: {}? Provide a decision: {}",
            "INTERNAL_ERROR": "Internal error due to {}. Decision: {}",
        }

    def get_prompt(self, type: str, layer_name: str, input_data):
        prompt = self.prompts.get(f"{type.upper()}_{layer_name.upper()}")
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
