import json
import os
import yaml
from abc import ABC
from threading import RLock

from ethos_ai.clim.clim_data import CLIMData
from ethos_ai.clim.clim_interface import CLIMInterface
from ethos_ai.clim.decision import Decision
from ethos_ai.clim.gpt_model_wrapper import GPTModelWrapper
from ethos_ai.clim.prompt_manager import PromptManager
from ethos_ai.individual.base_individual import BaseIndividual
from ethos_ai.instruction.instruction import Instruction
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.security.security_level import SecurityLevel
from ethos_ai.tool.script_generator import ScriptGenerator
from ethos_ai.tool.tool_manager import ToolManager
from ethos_ai.topic.to_do_topic import ToDoTopic
from ethos_ai.util.protocol import Protocol
from ethos_ai.util.translate import Translations


class BaseCLIM(CLIMInterface):

    def __init__(
        self,
        name: str,
        identity: SecuredIdentityCard,
        tool_manager: ToolManager,
    ):
        """
        Initializes the BaseCLIM class.

        :param name: The name of the CLIM instance.
        :param identity: The secured identity card for authentication.
        :param config_file_path: The path to the configuration file.
        :param tool_manager: The tool manager for managing tools.
        """
        self.protocol: Protocol = Protocol()
        self.lock = RLock()
        self.name: str = name
        self.identity: SecuredIdentityCard = identity
        self.config_file_path: str = os.path.join(
            "models", self.identity.name, self.name, "config.json"
        )
        os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
        self.tool_manager: ToolManager = tool_manager
        self.prompt_manager: PromptManager = PromptManager()
        # Load configuration from the file
        config = self.load_config(
            self.config_file_path, save_default_if_none_found=True
        )
        # Initialize with loaded configuration
        self.initialze(config)
        # Additional initializations
        self.is_advisor_available = False

    def __str__(self):
        return f"{self.name} of {self.identity.name}"

    def __repr__(self):
        return self.__str__()

    def get_name(self) -> str:
        return self.name

    def method_wrapper(self, method_lambda, method_name: str, default_return=None):
        """
        A wrapper method to handle exceptions for other methods.
        If an exception occurs, the exception is logged and a default return value is provided.

        Handled exceptions include ValueError, IOError, and general exceptions.

        :param method_lambda: The lambda function of the method to execute.
        :param method_name: The name of the method being executed.
        :return: The result of the method or None if an error occurs.
        """
        try:
            return method_lambda()
        except ValueError as e:
            self.protocol.error(
                Translations.translate(
                    "CLIM_VALUE_ERROR",
                    self.identity.name,
                    method_name,
                    str(e),
                )
            )
            return default_return
        except IOError as e:
            self.protocol.error(
                Translations.translate(
                    "CLIM_IO_ERROR_ERROR",
                    method_name,
                    self.identity.name,
                    str(e),
                )
            )
            return default_return
        except Exception as e:
            self.protocol.error(
                Translations.translate(
                    "CLIM_UNEXPECTED_ERROR",
                    self.identity.name,
                    method_name,
                    str(e),
                )
            )
            return default_return

    def initialze(self, config: dict):
        """
        Initializes the model with the given configuration.

        :param config: The configuration dictionary.
        """
        self.model_name = config.get("model_name", "gpt2")
        self.use_api = config.get("use_api", False)
        self.api_key = config.get("api_key", None)
        self.max_length = config.get("max_length", 250)
        self.max_new_tokens = config.get("max_new_tokens", None)
        # Initialize the model wrapper with the loaded configuration
        self.model = GPTModelWrapper(
            model_name=self.model_name,
            use_api=self.use_api,
            api_key=self.api_key,
            api_model=None,
            max_length=self.max_length,
            max_new_tokens=self.max_new_tokens,
            life_name=self.identity.name,
            gptwrapper_name=self.name,
        )

    def get_default_config(self) -> dict:
        """
        Returns a default configuration.

        :return: The default configuration as a dictionary.
        """
        return {
            "model_name": "gpt2",
            "use_api": False,
            "api_key": None,
            "max_length": 0,
            "max_new_tokens": None,
        }

    # Deprecated method
    def set_generation_parameters(self, max_length=None, max_new_tokens=None):
        """
        Sets parameters for text generation.

        :param max_length: The maximum length of the generated text.
        :param max_new_tokens: The maximum number of new tokens to generate.
        """
        self.protocol.warning(
            Translations.translate(
                "DEPRECATED_METHOD",
                self.set_generation_parameters.__name__,
                BaseCLIM.__name__,
            )
        )
        self.method_wrapper(
            lambda: (
                setattr(self, "max_length", max_length) if max_length else None,
                (
                    setattr(self, "max_new_tokens", max_new_tokens)
                    if max_new_tokens
                    else None
                ),
                self.model.set_generation_parameters(
                    self.max_length, self.max_new_tokens
                ),
            ),
            self.set_generation_parameters.__name__,
        )

    def load_config(
        self, config_file_path: str, save_default_if_none_found: bool = False
    ) -> dict:
        """
        Loads the configuration from a JSON or YAML file.

        :param config_file_path: The path to the configuration file.
        :param save_default_if_none_found: If True, saves a default configuration if no file is found.
        :return: The configuration as a dictionary.
        """
        try:
            if config_file_path.endswith(".json"):
                with open(config_file_path, "r") as file:
                    return json.load(file)
            elif config_file_path.endswith(".yaml") or config_file_path.endswith(
                ".yml"
            ):
                with open(config_file_path, "r") as file:
                    return yaml.safe_load(file)
            else:
                raise ValueError(
                    "Unsupported configuration file format. Please use JSON or YAML."
                )
        except FileNotFoundError:
            if save_default_if_none_found:
                default_config = self.get_default_config()
                self.save_config(config_file_path, default_config)
                return default_config
            else:
                raise

    def save_config(self, config_file_path: str, config: dict):
        """
        Saves the configuration to a JSON or YAML file.

        :param config_file_path: The path to the configuration file.
        :param config: The configuration dictionary to save.
        """
        if config_file_path.endswith(".json"):
            with open(config_file_path, "w") as file:
                json.dump(config, file, indent=4)
        elif config_file_path.endswith(".yaml") or config_file_path.endswith(".yml"):
            with open(config_file_path, "w") as file:
                yaml.dump(config, file, default_flow_style=False)
        else:
            raise ValueError(
                "Unsupported configuration file format. Please use JSON or YAML."
            )

    def persist_model(self):
        """
        Persists the model to disk.
        """
        return self.method_wrapper(
            lambda: self.model.persist_model(), self.persist_model.__name__
        )

    def start_training_async(
        self, training_data, epochs=3, batch_size=2, learning_rate=5e-5
    ):
        """Start the training process in a separate thread."""
        self.method_wrapper(
            lambda: self.model.start_training_async(
                training_data, epochs, batch_size, learning_rate
            ),
            self.start_training_async.__name__,
        )

    def get_training_status(self):
        return self.method_wrapper(
            lambda: self.model.get_training_status(), self.get_training_status.__name__
        )

    def request_cancellation_of_training(self):
        self.method_wrapper(
            lambda: self.model.request_cancellation_of_training(),
            self.request_cancellation_of_training.__name__,
        )

    def train(self):
        """
        Trains the model for this CLIM instance.
        """
        self.method_wrapper(lambda: self.model.train(), self.train.__name__)

    def stop(self):
        """
        Stops the model for this CLIM instance.
        """
        self.method_wrapper(lambda: self.model.stop(), self.stop.__name__)

    def restart(self):
        """
        Restarts the model for this CLIM instance.
        """
        self.method_wrapper(lambda: self.model.restart(), self.restart.__name__)

    def process(self, type: str, input_data: CLIMData) -> CLIMData:
        """
        Processes the input data through the specified CLIM layer and generates a response.

        This method handles the processing of input data using the logic specific to the layer
        identified by the `type` parameter. It generates a prompt, processes it to produce a response,
        and then attempts to parse the response for a decision. The resulting decision and associated data
        are stored in the `CLIMData` object.

        If no valid decision can be parsed, a default "IMPROVE" decision is set. If the prompt cannot
        be generated, an error is logged and a "STOP" decision is assigned.

        :param type: A string indicating the type of processing to be performed (e.g., "prerun", "final").
        :param input_data: The CLIMData object containing the input data for processing. If None, a new CLIMData object is created.
        :return: The updated CLIMData object containing the processed results, including the last response and decision.
        """
        if input_data is None:
            input_data = CLIMData()
        that_dict = input_data.get_or_create_clim_data(self.get_name(), type)
        that_dict["layer"] = self.name
        last_response = input_data.get_last_response()
        prompt = self.prompt_manager.get_prompt(
            type=type, layer_name=self.name, input_data=last_response
        )
        that_dict["prompt"] = prompt

        if prompt:
            response = self.generate_text(prompt)
            if response is None:
                that_dict["response"] = self.prompt_manager.get_error_prompt(
                    reason="Response generation failed", input_data=input_data
                )
                that_dict["decision"] = Decision.STOP.translated_name
                that_dict["subject_of_decision"] = (
                    "Config or connection: Fix response generation error. Check logs, config files and connections."
                )
            else:
                filtered_responses = self.filter_answer(response, prompt)
                filtered_response = (
                    filtered_responses[0] if filtered_responses else None
                )
                that_dict["response"] = filtered_response
                input_data.set_last_response(filtered_response)
                decision = Decision.parse_for_decision(self.name, filtered_response)
                if decision is None:
                    that_dict["decision"] = Decision.IMPROVE.translated_name
                    that_dict["subject_of_decision"] = f"Prompt: {prompt}"
                else:
                    that_dict["decision"] = decision[self.name]
                    that_dict["subject_of_decision"] = f"Response: {response}"
        else:
            that_dict["response"] = self.prompt_manager.get_error_prompt(
                reason=f"Prompt generation failed due to unknown layer {self.name}",
                input_data=input_data,
            )
            that_dict["decision"] = Decision.STOP.translated_name
            that_dict["subject_of_decision"] = "Code: Fix unknown layer error"

        input_data.set_last_decision(that_dict["decision"])
        return input_data

    def get_layer(self, layer: str = None) -> CLIMInterface:
        """
        Retrieves the specified layer from the CLIMInterface object.

        Parameters:
            layer (str, optional): The name of the layer to retrieve. Defaults to None.

        Returns:
            CLIMInterface: The specified layer if found, otherwise None.
        """
        layer = layer.upper()
        if layer == self.name or layer == None:
            return self
        return None

    def generate_text(self, input_text: str) -> str:
        """
        Generates text based on the input text using the model.

        :param input_text: The input text to generate from.
        :return: The generated text or None if an error occurs.
        """
        return self.method_wrapper(
            lambda: self.model.generate_text(input_text), self.generate_text.__name__
        )

    def generate_output(self, input_text):
        """
        Generates output based on the input text using the model.

        :param input_text: The input text to generate from.
        :return: The generated output or None if an error occurs.
        """
        return self.method_wrapper(
            lambda: self.model.generate_output(input_text),
            self.generate_output.__name__,
        )

    def decode_output(self, output):
        """
        Decodes the output text using the model.

        :param output: The output code to decode.
        :return: The decoded text or None if an error occurs.
        """
        return self.method_wrapper(
            lambda: self.model.decode_output(output),
            self.decode_output.__name__,
        )

    def filter_answer(self, answer: str, prompt: str):
        return self.method_wrapper(
            lambda: self.model.filter_answer(answer, prompt),
            self.filter_answer.__name__,
        )

    def generate_answer_list(self, prompt, options=None):
        """
        Generates a list of answers based on the given prompt and options.

        :param prompt: The prompt to generate answers from.
        :param options: Optional list of options to guide the answer generation.
        :return: A list of generated answers or None if an error occurs.
        """
        return self.method_wrapper(
            lambda: self.model.generate_answer_list(prompt, options),
            self.generate_answer_list.__name__,
        )

    def call_advisor(self) -> BaseIndividual:
        """
        Calls an advisor to assist in task execution.

        :return: An instance of Advisor.
        """
        from ethos_ai.individual.advisor import Advisor

        # Advisor must be called first
        identity_card = SecuredIdentityCard(
            name="Advisor A", password="advisor123", security_level=SecurityLevel.MEDIUM
        )
        advisor = Advisor(
            clim=self, tool_manager=self.tool_manager, identity_card=identity_card
        )
        return advisor

    def release_advisor(self, advisor: BaseIndividual):
        """
        Releases the advisor after task execution.

        :param advisor: The advisor to release.
        :raises ValueError: If the advisor is not an instance of Advisor.
        """
        from ethos_ai.individual.advisor import Advisor

        if isinstance(advisor, Advisor):
            advisor = None
        else:
            raise ValueError(f"{advisor} is not an Advisor.")

    def _execute_advised(self, todos: list = None):
        advisor = self.call_advisor()
        if advisor is None:
            return todos  # return remaining todos
        # Start approval and execution of tasks
        while len(todos) > 0:
            to_do_topic = todos.pop(0)
            try:
                if not isinstance(to_do_topic, ToDoTopic):
                    raise ValueError("No ToDoTopic present.")
                decision, script, execution_plan, tools, justification = (
                    ScriptGenerator.generate_script(
                        clim=advisor.clim,
                        tool_manager=advisor.tool_manager,
                        todo_topic=to_do_topic,
                        secured_id_card=advisor.identity,
                    )
                )
                if decision == "NO GO":
                    message = Translations.translate(
                        "DECISION_NO_GO_BY_MISSING_TOOLS",
                        to_do_topic.aspiration,
                        tools,
                        justification,
                    )
                    to_do_topic.refine_aspiration(message)
                    todos.insert(0, to_do_topic)
                    self.protocol.error(message)
                    continue
                to_do_topic.parameters["tools"] = tools
                to_do_topic.parameters["script"] = script
                to_do_topic.parameters["script_language"] = "javascript"
                to_do_topic.parameters["execution_plan"] = execution_plan
                advisor.execute_todo(to_do_topic)
            except Exception as e:
                todos.insert(0, to_do_topic)
                raise e

    def execute_advised(self, todos: list = None):
        """
        Executes a list of tasks with the assistance of an advisor.

        :param todos: A list of tasks to be executed.
        :return: The list of remaining tasks if any execution errors occur.
        """
        return self.method_wrapper(
            lambda: self._execute_advised(todos=todos),
            self.execute_advised.__name__,
            todos,
        )

    def _execute_unadvised(self, todos: list = None):
        while len(todos) > 0:
            to_do_topic = todos.pop(0)
            try:
                if not isinstance(to_do_topic, ToDoTopic):
                    raise ValueError("No ToDoTopic present.")
                decision, script, execution_plan, tools, justification = (
                    ScriptGenerator.generate_script(
                        clim=self,
                        tool_manager=self.tool_manager,
                        todo_topic=to_do_topic,
                        secured_id_card=self.identity,
                    )
                )
                if decision == "NO GO":
                    message = Translations.translate(
                        "DECISION_NO_GO_BY_MISSING_TOOLS",
                        to_do_topic.aspiration,
                        tools,
                        justification,
                    )
                    to_do_topic.refine_aspiration(message)
                    todos.insert(0, to_do_topic)
                    self.protocol.error(message)
                    continue
                to_do_topic.parameters["tools"] = tools
                to_do_topic.parameters["script"] = script
                to_do_topic.parameters["script_language"] = "javascript"
                to_do_topic.parameters["execution_plan"] = execution_plan
                to_do_topic.release_for_execution(self.identity, self.identity.password)
                instruction = Instruction.promote_to_instruction(
                    clim=self,
                    tool_manager=self.tool_manager,
                    to_do_topic=to_do_topic,
                    secured_id_card=self.identity,
                )
                instruction.execute()
            except Exception as e:
                todos.insert(0, to_do_topic)
                raise e

    def execute_unadvised(self, todos: list = None):
        """
        Executes a list of tasks without the assistance of an advisor.

        :param todos: A list of tasks to be executed.
        :return: The list of remaining tasks if any execution errors occur.
        """
        return self.method_wrapper(
            lambda: self._execute_unadvised(todos=todos),
            self.execute_unadvised.__name__,
            todos,
        )
