from typing import Dict, Optional, Union

"""
This class is used to store the data that is passed between the CLIM layers.
Methods:
- get_clim_datas(clim_name: str) -> Optional[Dict[str, Dict[str, str]]]: Retrieves the CLIM datas for a given clim_name.
- get_clim_data(clim_name: str, key: str) -> Optional[Dict[str, str]]: Retrieves a specific CLIM data for a given clim_name and key.
- get_or_create_clim_data(clim_name: str, key: str) -> Dict[str, str]: Retrieves or creates a specific CLIM data for a given clim_name and key.
- set_clim_datas(clim_name: str, value: Dict[str, Dict[str, str]]) -> None: Sets the CLIM datas for a given clim_name.
- set_clim_data(clim_name: str, key: str, value: Dict[str, str]) -> None: Sets a specific CLIM data for a given clim_name and key.
- get_last_response() -> Optional[str]: Retrieves the last response.
- set_last_response(response: str) -> None: Sets the last response.
- get_last_decision() -> Optional[str]: Retrieves the last decision.
- set_last_decision(decision: str) -> None: Sets the last decision.
- initialize_clim_data(clim_name: str) -> None: Initializes the CLIM data for a given clim_name if it doesn't exist.
"""


class CLIMData:
    def __init__(self):
        self.data: Dict[str, Union[str, Dict[str, Dict[str, str]]]] = {}

    # Getter and Setter for str data
    def get_clim_datas(self, clim_name: str) -> Optional[Dict[str, Dict[str, str]]]:
        return self.data.get(clim_name)

    def get_clim_data(self, clim_name: str, key: str) -> Optional[Dict[str, str]]:
        return self.get_clim_datas(clim_name).get(key)

    def get_or_create_clim_data(self, clim_name: str, key: str) -> Dict[str, str]:
        datas = self.data.setdefault(clim_name, {})
        return datas.setdefault(key, {})

    def set_clim_datas(self, clim_name: str, value: Dict[str, Dict[str, str]]) -> None:
        self.data[clim_name] = value

    def set_clim_data(self, clim_name: str, key: str, value: Dict[str, str]) -> None:
        datas = self.data.setdefault(clim_name, {})
        datas[key] = value

    # Getter and Setter for last_response
    def get_last_response(self) -> Optional[str]:
        return self.data.get("last_response")

    def set_last_response(self, response: str) -> None:
        self.data["last_response"] = response

    # Getter and Setter for last_decision
    def get_last_decision(self) -> Optional[str]:
        return self.data.get("last_decision")

    def set_last_decision(self, decision: str) -> None:
        self.data["last_decision"] = decision

    # Utility method to initialize str data if it doesn't exist
    def initialize_clim_data(self, clim_name: "str") -> None:
        if clim_name not in self.data:
            self.data[clim_name] = {}

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()
