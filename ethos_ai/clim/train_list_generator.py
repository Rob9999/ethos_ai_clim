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
