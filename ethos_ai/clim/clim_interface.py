# Definieren des CLIMInterface
from abc import ABC, abstractmethod

from ethos_ai.clim.clim_data import CLIMData
from ethos_ai.individual.base_individual import BaseIndividual
from ethos_ai.security.securied_identity_card import SecuredIdentityCard


class CLIMInterface(ABC):

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def process(self, type: str, input_data: CLIMData) -> CLIMData:
        pass

    @abstractmethod
    def generate_text(self, input_text: str) -> str:
        pass

    @abstractmethod
    def generate_output(self, input_text):
        pass

    @abstractmethod
    def decode_output(self, output) -> str:
        pass

    @abstractmethod
    def filter_answer(self, answer: str, prompt: str):
        pass

    @abstractmethod
    def generate_answer_list(self, prompt, options=None):
        pass

    @abstractmethod
    def persist_model(self):
        pass

    @abstractmethod
    def start_training_async(
        self, training_data, epochs=3, batch_size=2, learning_rate=5e-5
    ):
        """Start the training process in a separate thread."""
        pass

    @abstractmethod
    def get_training_status(self):
        """Return the current status of the training process."""
        pass

    @abstractmethod
    def request_cancellation_of_training(self):
        """Request to cancel the ongoing training."""
        pass

    @abstractmethod
    def train(self, training_data, epochs=3, batch_size=2, learning_rate=5e-5):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def restart(self):
        pass

    @abstractmethod
    def set_generation_parameters(self, max_length=None, max_new_tokens=None):
        pass

    @abstractmethod
    def call_advisor(self):
        pass

    @abstractmethod
    def release_advisor(self, advisor: BaseIndividual):
        pass

    @abstractmethod
    def execute_advised(self, todos: list = None):
        pass

    @abstractmethod
    def execute_unadvised(self, todos: list = None):
        pass

    @abstractmethod
    def get_layer(self, layer: str = None) -> "CLIMInterface":
        """Return in a multilayer CLIM a child CLIM or this layer."""
        return self
