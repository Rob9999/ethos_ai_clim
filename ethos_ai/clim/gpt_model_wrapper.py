import gc
import os
import threading
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, AdamW
from torch.utils.data import DataLoader
from tqdm import tqdm
import openai  # OpenAI API

from ethos_ai.clim.clim_data import CLIMData
from ethos_ai.clim.text_data_set import TextDataset
from ethos_ai.clim.training_status import TrainingStatus
from ethos_ai.individual.advisor import Advisor
from ethos_ai.clim.clim_interface import CLIMInterface
from ethos_ai.util.protocol import Protocol


class GPTModelWrapper(CLIMInterface):
    def __init__(
        self,
        model_name: str = "gpt2",
        use_api: bool = False,
        api_key: str = None,
        max_length: int = 50,
        max_new_tokens: int = None,
        api_model: str = "gpt-3.5-turbo",  # OpenAI API model (e.g., GPT-4, gpt-3.5-turbo)
        model_directory: str = "./models",  # Directory for personalized models
        life_name: str = "LIFE1",  # Default life entity (LIFE1, LIFE2, etc.)
        gptwrapper_name: str = "INDIVIDUAL",  # GPTWrapper for specific aspect (ETHIC, etc.)
    ):
        self.protocol = Protocol()
        self.model_name: str = model_name
        self.use_api: bool = use_api
        self.api_key: str = api_key
        self.max_length: int = max_length
        self.max_new_tokens: int = max_new_tokens
        self.api_model: str = api_model
        self.model_directory: str = model_directory
        self.life_name: str = life_name
        self.gptwrapper_name: str = gptwrapper_name
        self.status: TrainingStatus = TrainingStatus.NONE
        self.cancel_requested: bool = False
        self.changed: bool = False

        # Check for personalized finetuned model and load it
        self.model_path = os.path.join(
            self.model_directory, self.life_name, self.gptwrapper_name, self.model_name
        )
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        if not use_api:
            # Try to load a finetuned model
            try:
                self._load_model(self.model_path)
            except:
                self._create_model(self.model_name)
        else:
            if api_key is None:
                raise ValueError("API key must be provided when using OpenAI API.")
            openai.api_key = api_key
            self.model_name = model_name

    def _train_model(self, training_data, epochs=3, batch_size=2, learning_rate=5e-5):
        """Internal method to handle the actual training logic in a separate thread."""
        self.status = TrainingStatus.STARTED
        self.protocol.info(
            f"Training of {self.life_name}-{self.gptwrapper_name}: Initializing training process."
        )

        # Check if CUDA is available and move the model to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)
        self.protocol.info(
            f"Training of {self.life_name}-{self.gptwrapper_name}: Model moved to {device}."
        )

        # Prepare the dataset
        train_dataset = TextDataset(training_data, self.tokenizer)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Define optimizer
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        # Training loop
        self.model.train()
        self.protocol.info(
            f"Training of {self.life_name}-{self.gptwrapper_name}: Starting training loop."
        )
        try:
            self._training_loop(train_loader, optimizer, device, epochs)
            self.changed = True
        except Exception as e:
            self.protocol.error(
                f"Training of {self.life_name}-{self.gptwrapper_name} failed: {str(e)}"
            )
            self.status = TrainingStatus.FAILED
            return

        if not self.cancel_requested:
            self.status = TrainingStatus.STOPPED
            self.protocol.info(
                f"Training of {self.life_name}-{self.gptwrapper_name} completed."
            )
        else:
            self.protocol.info(
                f"Training of {self.life_name}-{self.gptwrapper_name} was canceled."
            )
            self.status = TrainingStatus.STOPPED

    def _training_loop(self, train_loader, optimizer, device, epochs):
        for epoch in range(epochs):
            if self.cancel_requested:
                self.status = TrainingStatus.CANCELLATION_IS_REQUESTED
                break
            epoch_loss = 0
            progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}")
            for batch in progress_bar:
                batch = batch.to(device)
                outputs = self.model(batch, labels=batch)
                loss = outputs.loss
                loss.backward()

                # Clip the gradients for stable training
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

                optimizer.step()
                optimizer.zero_grad()

                epoch_loss += loss.item()
                progress_bar.set_postfix({"loss": loss.item()})
            self.protocol.info(
                f"Training of {self.life_name}-{self.gptwrapper_name}: Epoch {epoch+1} completed with average loss: {epoch_loss / len(train_loader)}"
            )

    def _create_model(self, model_name):
        """Load base GPT-2 model if no finetuned model exists"""
        self.protocol.info(
            f"Creating model for {self.life_name}-{self.gptwrapper_name}."
        )
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.protocol.info(
            f"Base model loaded for {self.life_name}-{self.gptwrapper_name}."
        )
        self.changed = False
        return True

    def _load_model(self, model_path):
        """Load a model from a specified path."""
        self.model_path = model_path
        self.protocol.info(
            f"Loading finetuned model of {self.life_name}-{self.gptwrapper_name} from {self.model_path}."
        )
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_path)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_path)
        self.protocol.info(
            f"Finetuned model of {self.life_name}-{self.gptwrapper_name} loaded from {self.model_path}."
        )
        self.changed = False
        return True

    def _save_model(self, model_path):
        """Save the current model to a specified path."""
        self.protocol.info(
            f"Saving finetuned model of {self.life_name}-{self.gptwrapper_name} to {model_path}."
        )
        self.model.save_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        self.protocol.info(
            f"Finetuned model of {self.life_name}-{self.gptwrapper_name} saved to {model_path}."
        )
        self.changed = False
        return True

    def get_name(self) -> str:
        return f"{self.life_name}-{self.gptwrapper_name}-{self.model_name}"

    def persist_model(self):
        """Save the current model to the default path."""
        return self._save_model(self.model_path)

    def start_training_async(
        self, training_data, epochs=3, batch_size=2, learning_rate=5e-5
    ):
        """Start the training process in a separate thread."""
        if (
            self.status == TrainingStatus.STARTED
            or self.status == TrainingStatus.PENDING
        ):
            self.protocol.error("Training is already in progress.")
            return

        self.cancel_requested = False
        self.training_thread = threading.Thread(
            target=self._train_model,
            args=(training_data, epochs, batch_size, learning_rate),
        )
        self.training_thread.start()
        self.status = TrainingStatus.PENDING
        self.protocol.info(
            f"Training started for {self.life_name}-{self.gptwrapper_name}."
        )

    def request_cancellation_of_training(self):
        """Request to cancel the ongoing training."""
        if (
            self.status == TrainingStatus.STARTED
            or self.status == TrainingStatus.PENDING
        ):
            self.cancel_requested = True
            self.protocol.info(
                f"Cancellation requested for {self.life_name}-{self.gptwrapper_name}."
            )
        else:
            self.protocol.error(
                f"No active training to cancel for {self.life_name}-{self.gptwrapper_name}."
            )

    def get_training_status(self):
        """Return the current status of the training process."""
        return self.status

    def stop(self):
        """Stop the model."""
        self.protocol.info(f"Stopping {self.life_name}-{self.gptwrapper_name} model.")
        if self.changed:
            try:
                self.persist_model()
            except Exception as e:
                self.protocol.error(f"Error saving model: {str(e)}")
        del self.model
        self.model = None
        gc.collect()
        self.protocol.info(f"{self.life_name}-{self.gptwrapper_name} model stopped.")

    def restart(self):
        """Restart the model."""
        self.protocol.info(f"Restarting {self.life_name}-{self.gptwrapper_name} model.")
        if self.model is not None:
            self.stop()
        self.__init__(
            model_name=self.model_name,
            use_api=self.use_api,
            api_key=self.api_key,
            max_length=self.max_length,
            max_new_tokens=self.max_new_tokens,
            api_model=self.api_model,
            model_directory=self.model_directory,
            life_name=self.life_name,
            gptwrapper_name=self.gptwrapper_name,
        )
        self.protocol.info(f"{self.life_name}-{self.gptwrapper_name} model restarted.")

    def get_layer(self, layer: str = None) -> CLIMInterface:
        self.protocol.error(
            "Get layer is not supported for GPTModelWrapper. Please use a different model."
        )
        raise NotImplementedError

    def process(self, type: str, input_data: CLIMData) -> CLIMData:
        self.protocol.error(
            "Process is not supported for GPTModelWrapper. Please use a different model."
        )
        raise NotImplementedError

    def decode_output(self, output) -> str:
        if not self.use_api:
            return self.tokenizer.decode(output[0], skip_special_tokens=True)
        else:
            # Decode output from OpenAI API
            return output["choices"][0]["message"]["content"].strip()

    def generate_output(self, input_text):
        if not self.use_api:
            # Local model generation
            inputs = self.tokenizer(input_text, return_tensors="pt")
            if self.max_new_tokens:
                return self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
            else:
                max_length = (
                    self.max_length
                    if self.max_length > 0
                    else inputs["input_ids"].shape[-1] + 50
                )
                return self.model.generate(**inputs, max_length=max_length)
        else:
            # Use OpenAI API for text generation
            try:
                response = openai.ChatCompletion.create(
                    model=self.api_model,
                    messages=[{"role": "user", "content": input_text}],
                    max_tokens=self.max_length,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                return response
            except Exception as e:
                self.protocol.error(f"OpenAI API error: {str(e)}")
                return None

    def generate_text(self, input_text: str) -> str:
        outputs = self.generate_output(input_text)
        if outputs is not None:
            return self.decode_output(outputs)
        return "Error generating text."

    def filter_answer(self, answer: str, prompt: str):
        filtered = answer.replace(prompt + "\n", "").split("\n")
        filtered = [cleaned.strip() for cleaned in filtered if cleaned.strip()]
        return filtered

    def generate_answer_list(self, prompt, options=None):
        text = self.generate_text(prompt)
        return self.filter_answer(text, prompt)

    def set_generation_parameters(self, max_length=None, max_new_tokens=None):
        """Set parameters for text generation."""
        if max_length:
            self.max_length = max_length
        if max_new_tokens:
            self.max_new_tokens = max_new_tokens

    def call_advisor(self):
        self.protocol.error(
            "Call advisor is not supported for GPTModelWrapper. Please use a different model."
        )
        raise NotImplementedError

    def release_advisor(self, advisor: Advisor):
        self.protocol.error(
            "Release Advisor is not supported for GPTModelWrapper. Please use a different model."
        )
        raise NotImplementedError

    def train(self, training_data, epochs=3, batch_size=2, learning_rate=5e-5):
        if self.use_api:
            self.protocol.error("Training is only supported for local models, not API.")
            raise NotImplementedError

        self.protocol.info(f"Training of {self.name}: Initializing training process.")
        # Check if CUDA is available and move the model to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)

        self.protocol.info(f"Training of {self.name}: Preparing the dataset.")
        # Prepare the dataset
        train_dataset = TextDataset(training_data, self.tokenizer)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Define optimizer
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        self.protocol.info(f"Training of {self.name}: Starting training loop.")
        # Training loop
        self.model.train()
        for epoch in range(epochs):
            epoch_loss = 0
            progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}")
            for batch in progress_bar:
                batch = batch.to(device)
                outputs = self.model(batch, labels=batch)
                loss = outputs.loss
                loss.backward()

                optimizer.step()
                optimizer.zero_grad()

                epoch_loss += loss.item()
                progress_bar.set_postfix({"loss": loss.item()})

            self.protocol.info(
                f"Training of {self.name}: Epoch {epoch+1} completed with average loss: {epoch_loss / len(train_loader)}"
            )
        self.protocol.info(f"Training of {self.name}: Training completed.")

        # Save the fine-tuned model
        self.model.save_pretrained("./fine_tuned_gpt2")
        self.tokenizer.save_pretrained("./fine_tuned_gpt2")
        self.protocol.info(
            f"Training of {self.name}: Model saved to ./fine_tuned_gpt2."
        )

    def execute_advised(self, todos: list = None):
        self.protocol.error(
            "Advised execution is not supported for GPTModelWrapper. Please use a different model."
        )
        raise NotImplementedError

    def execute_unadvised(self, todos: list = None):
        self.protocol.error(
            "Unadvised execution is not supported for GPTModelWrapper. Please use a different model."
        )
        raise NotImplementedError
