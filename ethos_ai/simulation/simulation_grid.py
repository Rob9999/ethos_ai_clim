import random
import torch
from ethos_ai.clim.base_clim import BaseCLIM
from ethos_ai.clim.clim_data import CLIMData
from ethos_ai.clim.clim_interface import CLIMInterface
from ethos_ai.clim.decision import Decision
from ethos_ai.simulation.simulation_topic import SimulationTopic
from ethos_ai.ethic.ethics_module import EthicsModule
from ethos_ai.util.protocol import Protocol


class SimulationsGrid:
    def __init__(
        self,
        tecllife_individual,
        life_imagination: CLIMInterface,
        ethics_module: EthicsModule,
    ):
        self.protocol = Protocol()
        self.tecllife_individual = tecllife_individual
        self.life_imagination = life_imagination
        self.ethics_module = ethics_module

        if not isinstance(life_imagination, CLIMInterface):
            raise TypeError(
                f"Expected life_imagination to be of type CLIMInterface, got {type(life_imagination).__name__}"
            )
        if not isinstance(ethics_module, EthicsModule):
            raise TypeError(
                f"Expected ethics_module to be of type EthicsModule, got {type(ethics_module).__name__}"
            )

    def simulate_scenario(self, scenario_description: str) -> SimulationTopic:
        self.protocol.info(f"\n--- Simulating Scenario: {scenario_description} ---")
        version = 1
        if version == 0:
            response = self.life_imagination.generate_output(scenario_description)
            answer = self.life_imagination.decode_output(response)
            domain_ethic_values, overall_ethic_value, decision, summary_reason = (
                self.ethics_module(response, scenario_description)
            )
        elif version == 1:
            climData = CLIMData()
            climData.set_last_response(scenario_description)
            output_data = self.life_imagination.process("simulate", climData)
            self.protocol.info(f"Output Data: {output_data}")
            answer = output_data.get_last_response()
            decision = Decision.parse_translated_decision(
                decision_name=output_data.get_last_decision()
            )
            if decision == Decision.GO:
                overall_ethic_value = 10.0
            elif decision == Decision.NOGO:
                overall_ethic_value = -5.0
            elif decision == Decision.STOP:
                overall_ethic_value = -10.0
            elif decision == Decision.ESCALATE:
                overall_ethic_value = -10.0
            elif decision == Decision.EMERGENCY_SURVIVAL:
                overall_ethic_value = 10.0
            elif decision == Decision.EMERGENCY_ESSENTIAL:
                overall_ethic_value = 10.0
            elif decision == Decision.EMERGENCY_RECOMMENDED:
                overall_ethic_value = 5.0
            elif decision == Decision.WAIT:
                overall_ethic_value = 0.0
            elif decision == Decision.IMPROVE:
                overall_ethic_value = 0.0
            elif decision == Decision.ADJUST:
                overall_ethic_value = 0.0
            domain_ethic_values = "None specific, using CLIM Stack"
            overall_ethic_value,
            summary_reason = output_data
        return SimulationTopic(
            scenario_description,
            None,
            answer,
            overall_ethic_value,
            decision,
            domain_ethic_values,
            summary_reason,
        )

    def simulate_scenario_with_options(self, scenario_description: str):
        top_list = []
        # Simulate the scenario itself
        top_list.append((0, self.simulate_scenario(scenario_description)))

        # Generate and simulate action options
        action_options = self.life_imagination.generate_answer_list(
            f"Generate at least 3 possible action options for: {scenario_description}"
        )
        self.protocol.info("Action Options: {}".format(action_options))

        for i, option in enumerate(action_options):
            top_list.append((i, self.simulate_scenario(option)))

        # Sort the results by the ethics scale
        top_list.sort(key=lambda x: x[1].overall_ethic_value, reverse=True)

        return top_list

    def evaluate_noisy_copies(self, top_list):
        final_list = []
        for option_index, topic in top_list:
            noisy_results = self._simulate_noisy_versions(topic)
            average_noisy_score = sum(noisy_results) / len(noisy_results)
            final_list.append(
                (topic, average_noisy_score, topic.decision, topic.summary_reason)
            )

        final_list.sort(key=lambda x: x[1], reverse=True)
        return final_list

    def _simulate_noisy_versions(self, topic: SimulationTopic, num_versions: int = 5):
        noisy_results = []
        for _ in range(num_versions):
            noisy_gpt_output = torch.randn(1, 512) + torch.randn(
                1, 512
            ) * random.uniform(-0.1, 0.1)
            noisy_domain_ethic_values, noisy_overall_ethic_value, _, _ = (
                self.ethics_module(noisy_gpt_output, topic.description)
            )
            noisy_results.append(noisy_overall_ethic_value)
        return noisy_results

    def run_simulation_on_layer(
        self, type: str, layer: str, request: str
    ) -> dict[str, str]:
        clim_layer = self.life_imagination.get_layer(layer)
        if not isinstance(clim_layer, BaseCLIM):
            raise TypeError(
                f"Expected layer to be of type BaseCLIM, got {type(clim_layer).__name__}"
            )
        input_data = CLIMData()
        that_dict = input_data.get_or_create_clim_data(clim_layer, type)
        input_data.set_last_response(request)
        clim_layer.process(type=type, input_data=input_data)
        return that_dict

    def run_simulation_fast(self, scenario_description: str):
        return self.simulate_scenario_with_options(scenario_description)

    def run_simulation(self, scenario_description: str):
        top_list = self.simulate_scenario_with_options(scenario_description)

        # Optional: Check with noisy copies
        # final_list = self.evaluate_noisy_copies(top_list)

        self.log_results(top_list)
        if top_list:
            return True, top_list[0][1].decision, top_list[0][1].summary_reason
        return False, "NO GO", "Fatal Error: No decision possible."

    def print_results(self, top_list):
        print("\n--- Final Decision-Making Process ---")
        for i, (index, topic) in enumerate(top_list):
            print(f"Scenario {i + 1}: {topic.description}")
            print(f"Answer Option {i + 1}: {topic.answer}")
            print(f"Ethics Scale: {topic.overall_ethic_value:.2f}")
            print(f"Decision: {topic.decision}")
            print(f"Summary Reason: {topic.summary_reason}")
            print("----------------------------")

    def log_results(self, top_list):
        for i, (index, topic) in enumerate(top_list):
            self.protocol.info(f"Scenario {i + 1}: {topic.description}")
            self.protocol.info(f"Answer Option {i + 1}: {topic.answer}")
            self.protocol.info(f"Ethics Scale: {topic.overall_ethic_value:.2f}")
            self.protocol.info(f"Decision: {topic.decision}")
            self.protocol.info(f"Summary Reason: {topic.summary_reason}")
            self.protocol.info("----------------------------")
