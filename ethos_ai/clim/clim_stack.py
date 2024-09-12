from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from ethos_ai.clim.clim_interface import CLIMInterface
from ethos_ai.clim.base_clim import BaseCLIM
from ethos_ai.clim.clim_data import CLIMData
from ethos_ai.clim.decision import Decision
from ethos_ai.clim.ethic_clim import EthicCLIM
from ethos_ai.clim.individual_clim import IndividualCLIM
from ethos_ai.clim.ltclim import LTCLIM
from ethos_ai.clim.pipelines import Pipelines
from ethos_ai.clim.samt_clim import SAMTCLIM
from ethos_ai.individual.base_individual import BaseIndividual
from ethos_ai.instruction.instruction import Instruction
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.security.security_level import SecurityLevel
from ethos_ai.tool.script_generator import ScriptGenerator
from ethos_ai.tool.tool_manager import ToolManager
from ethos_ai.topic.to_do_topic import ToDoTopic
from ethos_ai.util.protocol import Protocol
from ethos_ai.util.translate import Translations


class CLIM(CLIMInterface):
    def __init__(
        self,
        identity_card: SecuredIdentityCard,
        password: str,
        tool_manager: ToolManager,
    ):
        self.protocol = Protocol()
        self.name: str = "Stacked CLIM"
        self.identity: SecuredIdentityCard = identity_card
        self.tool_manager: ToolManager = tool_manager
        self.ethic_layer: BaseCLIM = EthicCLIM(
            identity=identity_card, password=password, tool_manager=tool_manager
        )
        self.individual_layer: BaseCLIM = IndividualCLIM(
            identity=identity_card, password=password, tool_manager=tool_manager
        )
        self.samt_layer: BaseCLIM = SAMTCLIM(
            identity=identity_card, password=password, tool_manager=tool_manager
        )
        self.ltclim_layer: BaseCLIM = LTCLIM(
            identity=identity_card, password=password, tool_manager=tool_manager
        )

    def get_name(self) -> str:
        return self.name

    def process(self, type: str, input_data: CLIMData) -> CLIMData:
        """
        Processes the input data through a layered pipeline with emergency bypass capabilities.

        The process includes standard pipeline steps, such as ethic checks, individual adjustments,
        and both short-term and long-term optimizations. Additionally, the method can handle emergency
        situations by invoking specialized bypass stages based on the decision levels.

        :param input_data: The CLIMData object containing the input data for processing.
        :return: The final result of the processing pipeline.
        """

        that_dict = input_data.get_or_create_clim_data(self.get_name(), type)

        decision = None
        pipeline = Pipelines.standard_pipeline(
            ethic=self.ethic_layer,
            individual=self.individual_layer,
            samt=self.samt_layer,
            lclim=self.ltclim_layer,
        )
        while decision != Decision.STOP.translated_name:
            if decision is Decision.EMERGENCY_SURVIVAL.translated_name:
                pipeline = Pipelines.emergency_survival_pipeline(
                    ethic=self.ethic_layer, samt=self.samt_layer
                )
            elif decision is Decision.EMERGENCY_ESSENTIAL.translated_name:
                pipeline = Pipelines.emergency_essential_pipeline(
                    ethic=self.ethic_layer,
                    samt=self.samt_layer,
                    individual=self.individual_layer,
                )
            elif decision is Decision.EMERGENCY_RECOMMENDED.translated_name:
                pipeline = Pipelines.emergency_recommended_pipeline(
                    samt=self.samt_layer, individual=self.individual_layer
                )

            if not pipeline or pipeline == []:
                break
            type, clim = pipeline.pop(0)
            input_data = clim.process(type=type, input_data=input_data)
            decision = input_data.get_last_decision()
        return input_data

    def persist_model(self):
        """Persist the model to the file system."""
        self.protocol.info("Persisting model(s)...")
        success: bool = self.ethic_layer.persist_model() if True else False
        success: bool = (
            self.individual_layer.persist_model() if True else False and success
        )
        success: bool = self.samt_layer.persist_model() if True else False and success
        success: bool = self.ltclim_layer.persist_model() if True else False and success
        if success:
            self.protocol.info("Model(s) persisted.")
        else:
            self.protocol.error("Failed to persist model(s).")  # pragma: no cover

    def start_training_async(
        self, training_data, epochs=3, batch_size=2, learning_rate=5e-5
    ):
        """Start the training process in a separate thread."""
        self.protocol.info("Starting the CLIM model training asynchron...")
        if isinstance(training_data, dict):
            for key in training_data:
                if key == "ETHIC":
                    self.ethic_layer.start_training_async(
                        training_data[key], epochs, batch_size, learning_rate
                    )
                elif key == "INDIVIDUAL":
                    self.individual_layer.start_training_async(
                        training_data[key], epochs, batch_size, learning_rate
                    )
                elif key == "SAMT":
                    self.samt_layer.start_training_async(
                        training_data[key], epochs, batch_size, learning_rate
                    )
                elif key == "LTCLIM":
                    self.ltclim_layer.start_training_async(
                        training_data[key], epochs, batch_size, learning_rate
                    )
                else:
                    self.protocol.error(
                        f"Unknown training data for clim layer '{key}'. Training discarded."
                    )
        else:
            self.protocol.error(
                f"Invalid training data format: {type(training_data)}. Training aborted."
            )

    def train(self, training_data, epochs=3, batch_size=2, learning_rate=5e-5):
        """
        Trains the CLIM model using the input data.

        :param input_data: The CLIMData object containing the input data for training.
        :return: The updated CLIMData object after training.
        """
        self.protocol.info("Training the CLIM model...")
        if isinstance(training_data, dict):
            for key in training_data:
                if key == "ETHIC":
                    self.ethic_layer.train(
                        training_data[key], epochs, batch_size, learning_rate
                    )
                elif key == "INDIVIDUAL":
                    self.individual_layer.train(
                        training_data[key], epochs, batch_size, learning_rate
                    )
                elif key == "SAMT":
                    self.samt_layer.train(
                        training_data[key], epochs, batch_size, learning_rate
                    )
                elif key == "LTCLIM":
                    self.ltclim_layer.train(
                        training_data[key], epochs, batch_size, learning_rate
                    )
                else:
                    self.protocol.error(
                        f"Unknown training data for clim layer '{key}'. Training discarded."
                    )
        else:
            self.protocol.error(
                f"Invalid training data format: {type(training_data)}. Training aborted."
            )

    def get_training_status(self):
        """Return the current status of the training process."""
        return {
            "ETHIC": self.ethic_layer.get_training_status(),
            "INDIVIDUAL": self.individual_layer.get_training_status(),
            "SAMT": self.samt_layer.get_training_status(),
            "LTCLIM": self.ltclim_layer.get_training_status(),
        }

    def request_cancellation_of_training(self):
        """Request to cancel the ongoing training."""
        self.ethic_layer.request_cancellation_of_training()
        self.individual_layer.request_cancellation_of_training()
        self.samt_layer.request_cancellation_of_training()
        self.ltclim_layer.request_cancellation_of_training()

    def stop(self):
        """Stop the clim stack."""
        self.ethic_layer.stop()
        self.individual_layer.stop()
        self.samt_layer.stop()
        self.ltclim_layer.stop()

    def restart(self):
        """Restart the clim stack."""
        self.ethic_layer.restart()
        self.individual_layer.restart()
        self.samt_layer.restart()
        self.ltclim_layer.restart()

    def get_layer(self, layer: str = None) -> CLIMInterface:
        """
        Retrieves the specified layer from the CLIMInterface object.

        Parameters:
            layer (str): The name of the layer to retrieve. Valid options are "ETHIC", "INDIVIDUAL", "SAMT", and "LTCLIM".

        Returns:
            CLIMInterface: The requested layer as a CLIMInterface object, or None if the layer is not found.
        """
        layer = layer.upper()
        if layer == "ETHIC":
            return self.ethic_layer
        elif layer == "INDIVIDUAL":
            return self.individual_layer
        elif layer == "SAMT":
            return self.samt_layer
        elif layer == "LTCLIM":
            return self.ltclim_layer
        else:
            return None

    def generate_text(self, input_text: str) -> str:
        """
        Generates text based on the input text.

        :param input_text: The input text to generate text from.
        :return: The generated text.
        """
        answers = ("\n").join(
            [
                layer.generate_text(input_text)
                for layer in [
                    self.ethic_layer,
                    self.individual_layer,
                    self.samt_layer,
                    self.ltclim_layer,
                ]
            ]
        )
        return answers

    def generate_output(self, input_text):
        """
        Generates output based on the input text.

        :param input_text: The input text to generate output from.
        :return: The generated output.
        """
        answers = dict()
        answers["ETHIC"] = self.ethic_layer.generate_output(input_text)
        answers["INDIVIDUAL"] = self.individual_layer.generate_output(input_text)
        answers["SAMT"] = self.samt_layer.generate_output(input_text)
        answers["LTCLIM"] = self.ltclim_layer.generate_output(input_text)
        return answers

    def decode_output(self, output) -> str:
        """
        Decodes the output text.

        :param output: The output code to decode.
        :return: The decoded output text.
        """
        if isinstance(output, dict):
            answers = ""
            for layer in [
                self.ethic_layer,
                self.individual_layer,
                self.samt_layer,
                self.ltclim_layer,
            ]:
                if layer.name in output:
                    answers += layer.decode_output(output[layer.name])
            return answers
        return ""

    def filter_answer(self, answer: str, prompt: str):
        """
        Filters the answer based on the prompt.

        :param answer: The answer to filter.
        :param prompt: The prompt to filter the answer with.
        :return: The filtered answer.
        """
        raise NotImplementedError("Method not implemented")

    def generate_answer_list(self, prompt, options=None):
        """
        Generates a list of answers based on the prompt and options.

        :param prompt: The prompt for generating answers.
        :param options: The options for generating answers.
        :return: The list of generated answers.
        """
        answers = ("\n").join(
            [
                layer.generate_answer_list(prompt=prompt, options=options)
                for layer in [
                    self.ethic_layer,
                    self.individual_layer,
                    self.samt_layer,
                    self.ltclim_layer,
                ]
            ]
        )
        return answers

    def set_generation_parameters(self, max_length=None, max_new_tokens=None):
        """
        Sets the generation parameters for text generation.

        :param max_length: The maximum length of the generated text.
        :param max_new_tokens: The maximum number of new tokens allowed in the generated text.
        """
        raise NotImplementedError("Method not implemented")

    def call_advisor(self):
        """
        Calls the advisor for guidance.
        """
        # Implement your code here
        raise NotImplementedError("Method not implemented")

    def release_advisor(self, advisor: BaseIndividual):
        """
        Releases the advisor.

        :param advisor: The advisor to release.
        """
        # Implement your code here
        raise NotImplementedError("Method not implemented")

    def execute_advised(self, todos: list = None):
        """
        Executes the advised actions.

        :param todos: The list of actions to execute.
        """
        # Implement your code here
        raise NotImplementedError("Method not implemented")

    def execute_unadvised(self, todos: list = None):
        """
        Executes the unadvised actions.

        :param todos: The list of actions to execute.
        """
        # Implement your code here
        raise NotImplementedError("Method not implemented")
