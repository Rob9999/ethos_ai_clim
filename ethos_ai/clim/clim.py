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
from ethos_ai.instruction.instruction import Instruction
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.security.security_level import SecurityLevel
from ethos_ai.tool.script_generator import ScriptGenerator
from ethos_ai.tool.tool_manager import ToolManager
from ethos_ai.topic.to_do_topic import ToDoTopic
from ethos_ai.util.translate import Translations


class CLIM(BaseCLIM):
    def __init__(
        self,
        identity_card: SecuredIdentityCard,
        password: str,
        tool_manager: ToolManager,
    ):
        super().__init__(
            name="MAIN",
            identity=identity_card,
            tool_manager=tool_manager,
        )
        self.ethic_layer: BaseCLIM = EthicCLIM(
            identity=identity_card, password=password, tool_manager=tool_manager
        )
        self.individual_layer: BaseCLIM = IndividualCLIM(
            identity=identity_card, password=password, tool_manager=tool_manager
        )
        self.samt_layer: BaseCLIM = SAMTCLIM(
            identity=identity_card, password=password, tool_manager=tool_manager
        )
        self.lclim_layer: BaseCLIM = LTCLIM(
            identity=identity_card, password=password, tool_manager=tool_manager
        )

    def process(self, type: str, input_data: CLIMData) -> CLIMData:
        """
        Processes the input data through a layered pipeline with emergency bypass capabilities.

        The process includes standard pipeline steps, such as ethic checks, individual adjustments,
        and both short-term and long-term optimizations. Additionally, the method can handle emergency
        situations by invoking specialized bypass stages based on the decision levels.

        :param input_data: The CLIMData object containing the input data for processing.
        :return: The final result of the processing pipeline.
        """

        that_dict = input_data.get_or_create_clim_data(self, type)

        decision = None
        pipeline = Pipelines.standard_pipeline(
            ethic=self.ethic_layer,
            individual=self.individual_layer,
            samt=self.samt_layer,
            lclim=self.lclim_layer,
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
        errors = []
        self.protocol.info("Persisting model(s)...")
        try:
            self.ethic_layer.persist_model()
        except Exception as e:
            errors.append(f"ETHIC: {e}")
        try:
            self.individual_layer.persist_model()
        except Exception as e:
            errors.append(f"INDIVIDUAL: {e}")
        try:
            self.samt_layer.persist_model()
        except Exception as e:
            errors.append(f"SAMT: {e}")
        try:
            self.lclim_layer.persist_model()
        except Exception as e:
            errors.append(f"LTCLIM: {e}")
        if errors:
            self.protocol.error(f"Error(s) persisting model: {errors}")
            raise Exception(f"Error(s) persisting model: {errors}")
        self.protocol.info("Model(s) persisted.")

    def start_training_async(
        self, training_data, epochs=3, batch_size=2, learning_rate=5e-5
    ):
        """Start the training process in a separate thread."""
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
                    self.lclim_layer.start_training_async(
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
            "LTCLIM": self.lclim_layer.get_training_status(),
        }

    def request_cancellation_of_training(self):
        """Request to cancel the ongoing training."""
        self.ethic_layer.request_cancellation_of_training()
        self.individual_layer.request_cancellation_of_training()
        self.samt_layer.request_cancellation_of_training()
        self.lclim_layer.request_cancellation_of_training()

    def restart(self):
        super().restart()
        self.ethic_layer.restart()
        self.individual_layer.restart()
        self.samt_layer.restart()
        self.lclim_layer.restart()
