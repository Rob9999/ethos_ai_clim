import gc
import os
import shutil
import threading
import time
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
        start_model: bool = True,  # Start the model on initialization
    ):
        self.protocol = Protocol()
        self._model_name: str = model_name
        self._use_api: bool = use_api
        self._api_key: str = api_key
        self._max_length: int = max_length
        self._max_new_tokens: int = max_new_tokens
        self._api_model: str = api_model
        self._model_directory: str = model_directory
        self._life_name: str = life_name
        self._gptwrapper_name: str = gptwrapper_name
        self._start_model: bool = start_model
        self._status: TrainingStatus = TrainingStatus.NONE
        self._cancel_requested: bool = False
        self._changed: bool = False
        self._model = None

        # Check for personalized finetuned model and load it
        self.model_path = os.path.join(
            self._model_directory,
            self._life_name,
            self._gptwrapper_name,
            self._model_name,
        )
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        if self._start_model:
            self._start()

    def _train_model(self, training_data, epochs=3, batch_size=2, learning_rate=5e-5):
        """Internal method to handle the actual training logic in a separate thread."""
        self._status = TrainingStatus.STARTED
        self.protocol.info(
            f"Training of {self._life_name}-{self._gptwrapper_name}: Initializing training process."
        )

        # Check if CUDA is available and move the model to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model.to(device)
        self.protocol.info(
            f"Training of {self._life_name}-{self._gptwrapper_name}: Model moved to {device}."
        )

        # Prepare the dataset
        train_dataset = TextDataset(training_data, self.tokenizer)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Define optimizer
        optimizer = AdamW(self._model.parameters(), lr=learning_rate)

        # Training loop
        self._model.train()
        self.protocol.info(
            f"Training of {self._life_name}-{self._gptwrapper_name}: Starting training loop."
        )
        try:
            self._training_loop(train_loader, optimizer, device, epochs)
            self._changed = True
        except Exception as e:
            self.protocol.error(
                f"Training of {self._life_name}-{self._gptwrapper_name} failed: {str(e)}"
            )
            self._status = TrainingStatus.FAILED
            return

        if not self._cancel_requested:
            self._status = TrainingStatus.STOPPED
            self.protocol.info(
                f"Training of {self._life_name}-{self._gptwrapper_name} completed."
            )
        else:
            self.protocol.info(
                f"Training of {self._life_name}-{self._gptwrapper_name} was canceled."
            )
            self._status = TrainingStatus.STOPPED

    def _training_loop(self, train_loader, optimizer, device, epochs):
        for epoch in range(epochs):
            if self._cancel_requested:
                self._status = TrainingStatus.CANCELLATION_IS_REQUESTED
                break
            epoch_loss = 0
            progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}")
            for batch in progress_bar:
                batch = batch.to(device)
                outputs = self._model(batch, labels=batch)
                loss = outputs.loss
                loss.backward()

                # Clip the gradients for stable training
                torch.nn.utils.clip_grad_norm_(self._model.parameters(), max_norm=1.0)

                optimizer.step()
                optimizer.zero_grad()

                epoch_loss += loss.item()
                progress_bar.set_postfix({"loss": loss.item()})
            self.protocol.info(
                f"Training of {self._life_name}-{self._gptwrapper_name}: Epoch {epoch+1} completed with average loss: {epoch_loss / len(train_loader)}"
            )

    def _create_model(self, model_name):
        """Load base GPT-2 model if no finetuned model exists"""
        self.protocol.info(
            f"Creating model for {self._life_name}-{self._gptwrapper_name}."
        )
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self._model = GPT2LMHeadModel.from_pretrained(model_name)
        self.protocol.info(
            f"Base model loaded for {self._life_name}-{self._gptwrapper_name}."
        )
        self._changed = False
        return True

        # Work Fix for model lib bug: Save a model to a path, while a model is already saved to this path, fails
        # Work Fix:
        #           Save the current model to the backup path, and when loading the model again overwrite the model
        #           path with the backup model path and then load from model path.

    def _work_fix_overwite_model_with_backup_model_and_then_loadbecause_save_model_bug(
        self, model_path
    ):
        """Work Fix: Save the current model to a specified path, when a model is already saved to this path.

        1. Saving is done to a backup path.
        2. Before loading the existing model check for backup path, and if so, overwrite the existing model with the backup model.
        3. Then load the model.
        """

    def _load_model(self, model_path):
        """Load a model from a specified path."""
        self.model_path = model_path
        self.protocol.info(
            f"Loading finetuned model of {self._life_name}-{self._gptwrapper_name} from {self.model_path}."
        )
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_path)
        self._model = GPT2LMHeadModel.from_pretrained(self.model_path)
        self.protocol.info(
            f"Finetuned model of {self._life_name}-{self._gptwrapper_name} loaded from {self.model_path}."
        )
        self._changed = False
        return True

    def _save_model(self, model_path):
        """Save the current model to a specified path."""
        self.protocol.info(
            f"Saving finetuned model of {self._life_name}-{self._gptwrapper_name} to {model_path}."
        )
        self._model.save_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        self.protocol.info(
            f"Finetuned model of {self._life_name}-{self._gptwrapper_name} saved to {model_path}."
        )
        self._changed = False
        return True

    def get_name(self) -> str:
        return f"{self._life_name}-{self._gptwrapper_name}-{self._model_name}"

    def persist_model(self):
        """Persist the model to the disk."""
        try:
            # Attempt to save the model to the main path
            return self._save_model(self.model_path)
        except Exception as e:
            # Check if the model path is not empty
            if os.path.exists(self.model_path) and os.listdir(self.model_path):
                # Workaround for the model library bug:
                # Saving a model to a path where a model already exists fails.
                # Workaround steps:
                # - Save the current model to a backup path.
                # - Remove the original model path.
                # - Rename the backup path to the original model path.

                # Backup path for the model
                model_path_backup = self.model_path + "_backup_" + str(time.time())

                # Ensure backup directory exists before proceeding
                if not os.path.exists(model_path_backup):
                    os.makedirs(model_path_backup)

                # Save the model to the backup path
                success = self._save_model(model_path_backup)

                if success:
                    # If backup is successful, replace the model path with the backup
                    if os.path.exists(self.model_path):
                        # Remove the old model directory
                        shutil.rmtree(self.model_path)

                    # Move the backup model to the original model path
                    os.rename(model_path_backup, self.model_path)

                    return success
            # If the directory wasn't found or another error occurred, re-raise the exception
            raise e

    def start_training_async(
        self, training_data, epochs=3, batch_size=2, learning_rate=5e-5
    ):
        """Start the training process in a separate thread."""
        if (
            self._status == TrainingStatus.STARTED
            or self._status == TrainingStatus.PENDING
        ):
            self.protocol.error("Training is already in progress.")
            return

        self._cancel_requested = False
        self.training_thread = threading.Thread(
            target=self._train_model,
            args=(training_data, epochs, batch_size, learning_rate),
        )
        self.training_thread.start()
        self._status = TrainingStatus.PENDING
        self.protocol.info(
            f"Training started for {self._life_name}-{self._gptwrapper_name}."
        )

    def request_cancellation_of_training(self):
        """Request to cancel the ongoing training."""
        if (
            self._status == TrainingStatus.STARTED
            or self._status == TrainingStatus.PENDING
        ):
            self._cancel_requested = True
            self.protocol.info(
                f"Cancellation requested for {self._life_name}-{self._gptwrapper_name}."
            )
        else:
            self.protocol.error(
                f"No active training to cancel for {self._life_name}-{self._gptwrapper_name}."
            )

    def get_training_status(self):
        """Return the current status of the training process."""
        return self._status

    def _start(self):
        if not self._use_api:
            # Try to load a finetuned model
            try:
                if os.listdir(self.model_path):
                    self._load_model(self.model_path)
                    return
            except Exception as e:
                self.protocol.error(f"Error loading model: {str(e)}")
            self._create_model(self._model_name)
            return
        else:
            if self._api_key is None:
                raise ValueError("API key must be provided when using OpenAI API.")
            openai.api_key = self._api_key
            self._model_name = self._model_name

    def start(self):
        """Start the model."""
        self.protocol.info(f"Starting {self._life_name}-{self._gptwrapper_name} model.")
        if self._model is not None:
            self.stop()
        self._start()
        self.protocol.info(f"{self._life_name}-{self._gptwrapper_name} model started.")

    def stop(self):
        """Stop the model."""
        self.protocol.info(f"Stopping {self._life_name}-{self._gptwrapper_name} model.")
        if self._changed:
            try:
                self.persist_model()
            except Exception as e:
                self.protocol.error(f"Error saving model: {str(e)}")
        del self._model
        self._model = None
        gc.collect()
        self.protocol.info(f"{self._life_name}-{self._gptwrapper_name} model stopped.")

    def restart(self):
        """Restart the model."""
        self.protocol.info(
            f"Restarting {self._life_name}-{self._gptwrapper_name} model."
        )
        if self._model is not None:
            self.stop()
        self._start()
        self.protocol.info(
            f"{self._life_name}-{self._gptwrapper_name} model restarted."
        )

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
        if not self._use_api:
            return self.tokenizer.decode(output[0], skip_special_tokens=True)
        else:
            # Decode output from OpenAI API
            return output["choices"][0]["message"]["content"].strip()

    def generate_output(self, input_text):
        if not self._use_api:
            # Local model generation
            inputs = self.tokenizer(input_text, return_tensors="pt")
            if self._max_new_tokens:
                return self._model.generate(
                    **inputs, max_new_tokens=self._max_new_tokens
                )
            else:
                max_length = (
                    self._max_length
                    if self._max_length > 0
                    else inputs["input_ids"].shape[-1] + 50
                )
                return self._model.generate(**inputs, max_length=max_length)
        else:
            # Use OpenAI API for text generation
            try:
                response = openai.ChatCompletion.create(
                    model=self._api_model,
                    messages=[{"role": "user", "content": input_text}],
                    max_tokens=self._max_length,
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
            self._max_length = max_length
        if max_new_tokens:
            self._max_new_tokens = max_new_tokens

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
        if self._use_api:
            self.protocol.error("Training is only supported for local models, not API.")
            raise NotImplementedError

        self.protocol.info(f"Training of {self.name}: Initializing training process.")
        # Check if CUDA is available and move the model to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model.to(device)

        self.protocol.info(f"Training of {self.name}: Preparing the dataset.")
        # Prepare the dataset
        train_dataset = TextDataset(training_data, self.tokenizer)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Define optimizer
        optimizer = AdamW(self._model.parameters(), lr=learning_rate)

        self.protocol.info(f"Training of {self.name}: Starting training loop.")
        # Training loop
        self._model.train()
        for epoch in range(epochs):
            epoch_loss = 0
            progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}")
            for batch in progress_bar:
                batch = batch.to(device)
                outputs = self._model(batch, labels=batch)
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
        self._model.save_pretrained("./fine_tuned_gpt2")
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
