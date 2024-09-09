from typing import Dict, Optional, Union

from ethos_ai.clim.clim_interface import CLIMInterface


class CLIMData:
    def __init__(self):
        self.data: Dict[
            Union[str, CLIMInterface], Union[str, Dict[str, Dict[str, str]]]
        ] = {}

    # Getter and Setter for CLIMInterface data
    def get_clim_datas(
        self, clim_instance: CLIMInterface
    ) -> Optional[Dict[str, Dict[str, str]]]:
        return self.data.get(clim_instance)

    def get_clim_data(
        self, clim_instance: CLIMInterface, key: str
    ) -> Optional[Dict[str, str]]:
        return self.get_clim_datas(clim_instance).get(key)

    def get_or_create_clim_data(
        self, clim_instance: CLIMInterface, key: str
    ) -> Dict[str, str]:
        datas = self.data.setdefault(clim_instance, {})
        return datas.setdefault(key, {})

    def set_clim_datas(
        self, clim_instance: CLIMInterface, value: Dict[str, Dict[str, str]]
    ) -> None:
        self.data[clim_instance] = value

    def set_clim_data(
        self, clim_instance: CLIMInterface, key: str, value: Dict[str, str]
    ) -> None:
        datas = self.data.setdefault(clim_instance, {})
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

    # Utility method to initialize CLIMInterface data if it doesn't exist
    def initialize_clim_data(self, clim_instance: "CLIMInterface") -> None:
        if clim_instance not in self.data:
            self.data[clim_instance] = {}

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()
