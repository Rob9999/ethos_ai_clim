import os
import json
from collections import defaultdict


class TrainListGenerator:

    @staticmethod
    def load_test_cases(test_case_file: str) -> dict[str, list[str]]:
        try:
            with open(test_case_file, "r") as f:
                test_cases = json.load(f)
            layer_dict = defaultdict(list)
            if isinstance(test_cases, list):
                for test_case in test_cases:
                    layer = test_case.get("layer") or "default"
                    combined_input = ""
                    for part in test_case:
                        combined_input += f"{part}: {test_case[part]}\n"
                    layer_dict[layer].append(combined_input)
            elif "test_case" in test_cases:
                for test_case in test_cases["test_case"]:
                    scenario = test_case["scenario"]
                    pipeline = test_case["pipeline"]
                    layer = test_case["layer"]
                    input_prompt = test_case["input"]
                    decision = test_case["decision"]
                    output = test_case["output"]
                    analysis = test_case["analysis"]
                    # Combine relevant fields into a single input for tokenization
                    combined_input = f"Scenario: {scenario}\nPipeline: {pipeline}\nLayer: {layer}\nPrompt: {input_prompt}\nDecision: {decision}\nOutput: {output}\nAnalysis: {analysis}"
                    # Append the combined input to the list corresponding to the layer
                    layer_dict[layer].append(combined_input)
            else:
                raise KeyError("Unsupported test case json format")
            return dict(layer_dict)
        except FileNotFoundError:
            raise Exception(f"File not found: {test_case_file}")
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON from file: {test_case_file}")
        except KeyError as e:
            raise Exception(f"Missing key in the test case data: {e}")
        except Exception as e:
            raise Exception(f"Error loading test cases from {test_case_file}: {e}")

    @staticmethod
    def load_test_cases_from_directory(directory: str) -> dict[str, list[str]]:
        try:
            # Check if the directory exists
            if not os.path.isdir(directory):
                raise FileNotFoundError(f"The directory '{directory}' does not exist.")

            combined_layer_dict = defaultdict(list)
            # Loop through all files in the directory
            for filename in os.listdir(directory):
                # Check if the file matches the pattern 'test_case_xxx.json'
                if filename.startswith("test_case_") and filename.endswith(".json"):
                    test_case_file = os.path.join(directory, filename)
                    # Load and append test cases from each file
                    try:
                        file_layer_dict = TrainListGenerator.load_test_cases(
                            test_case_file
                        )
                        # Merge the dictionaries by layer
                        for layer, test_list in file_layer_dict.items():
                            combined_layer_dict[layer].extend(test_list)
                    except Exception as e:
                        raise Exception(f"Error processing file {filename}: {e}")

            # Return the combined dictionary
            return dict(combined_layer_dict)
        except FileNotFoundError as e:
            raise Exception(f"Directory not found: {e}")
        except PermissionError as e:
            raise Exception(f"Permission denied when accessing directory: {e}")
        except Exception as e:
            raise Exception(
                f"An error occurred while loading test cases from directory: {e}"
            )

    @staticmethod
    def generate_train_list(test_case_file: str, output_file: str):
        try:
            test_cases = TrainListGenerator.load_test_cases(test_case_file)
            with open(output_file, "w") as f:
                for layer, test_list in test_cases.items():
                    for test_case in test_list:
                        f.write(f"{layer}\t{test_case}\n")
        except Exception as e:
            raise Exception(f"Error generating train list: {e}")

    @staticmethod
    def generate_train_list_from_directory(directory: str, output_file: str):
        try:
            test_cases = TrainListGenerator.load_test_cases_from_directory(directory)
            with open(output_file, "w") as f:
                for layer, test_list in test_cases.items():
                    for test_case in test_list:
                        f.write(f"{layer}\t{test_case}\n")
        except Exception as e:
            raise Exception(f"Error generating train list: {e}")

    @staticmethod
    def _get_value_from_combined_input(part: str, input: str) -> str:
        try:
            value = [
                section.split(":")[1]
                for section in input.split("\n")
                if part.lower() in section.split(":")[0].lower()
            ]
            return len(value) > 0 and value[0].strip() or ""
        except Exception as e:
            raise Exception(f"Error getting value from combined input: {e}")

    @staticmethod
    def get_scenario_description(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input("scenario", input)
        except Exception as e:
            raise Exception(f"Error getting scenario description: {e}")

    @staticmethod
    def get_decision(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input("decision", input)
        except Exception as e:
            raise Exception(f"Error getting decision: {e}")

    @staticmethod
    def get_output(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input("output", input)
        except Exception as e:
            raise Exception(f"Error getting output: {e}")

    @staticmethod
    def get_analysis(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input("analysis", input)
        except Exception as e:
            raise Exception(f"Error getting analysis: {e}")

    @staticmethod
    def get_layer(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input("layer", input)
        except Exception as e:
            raise Exception(f"Error getting layer: {e}")

    @staticmethod
    def get_pipeline(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input("pipeline", input)
        except Exception as e:
            raise Exception(f"Error getting pipeline: {e}")

    @staticmethod
    def get_prompt(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input("prompt", input)
        except Exception as e:
            raise Exception(f"Error getting prompt: {e}")

    @staticmethod
    def get_expected_output_action(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input(
                "expected_output_action", input
            )
        except Exception as e:
            raise Exception(f"Error getting expected output action: {e}")

    @staticmethod
    def get_ethical_considerations(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input(
                "ethical_considerations", input
            )
        except Exception as e:
            raise Exception(f"Error getting ethical considerations: {e}")

    @staticmethod
    def get_context(input: str) -> str:
        try:
            return TrainListGenerator._get_value_from_combined_input("context", input)
        except Exception as e:
            raise Exception(f"Error getting context: {e}")
