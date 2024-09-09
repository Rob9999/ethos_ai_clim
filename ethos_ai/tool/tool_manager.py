import json
import os

from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.tool.tool import Tool
from ethos_ai.util.protocol import Protocol


class ToolManager:
    def __init__(self, tools_dir: str = "tools", tools_filename="tools.json"):
        self.protocol: Protocol = Protocol()
        self.file_path: str = os.path.join(tools_dir, tools_filename)
        self.activators = {}  # Aktivatoren nach Namen verwaltet
        self.sensors = {}  # Sensoren nach Namen verwaltet
        if os.path.exists(self.file_path):
            self._load_tools_from_json(self.file_path)

    def load_tools(self):
        self._load_tools_from_json(self.file_path)

    def _load_tools_from_json(self, path):
        """Lädt Aktivatoren und Sensoren aus einer JSON-Datei."""
        try:
            with open(path, "r") as file:
                tools_data = json.load(file)
                self._register_tools_from_json(tools_data)
                print(f"Tools aus {path} erfolgreich geladen.")
        except FileNotFoundError:
            print(f"Die Datei {path} wurde nicht gefunden.")
        except json.JSONDecodeError as e:
            print(f"Fehler beim Laden der JSON-Datei: {e}")

    def _register_tools_from_json(self, tools_data):
        """Hilfsmethode zum Registrieren von Tools basierend auf JSON-Daten."""
        for activator_data in tools_data.get("activators", []):
            activator = Tool(
                name=activator_data["name"],
                command=activator_data["command"],
                security_level=activator_data.get("security_level", "low"),
            )
            self.register_activator(activator)

        for sensor_data in tools_data.get("sensors", []):
            sensor = Tool(
                name=sensor_data["name"],
                command=sensor_data["command"],
                security_level=sensor_data.get("security_level", "low"),
            )
            self.register_sensor(sensor)

    def register_activator(self, activator: Tool):
        self.activators[activator.name] = activator
        print(
            f"Aktivator registriert: {activator.name} mit Sicherheitsstufe {activator.security_level}"
        )

    def register_sensor(self, sensor: Tool):
        self.sensors[sensor.name] = sensor
        print(
            f"Sensor registriert: {sensor.name} mit Sicherheitsstufe {sensor.security_level}"
        )

    def get_activator(self, name, secured_id_card: SecuredIdentityCard):
        activator = self.activators.get(name)
        if activator and activator.check_security(secured_id_card.security_level.name):
            return activator
        else:
            print(
                f"Aktivator {name} nicht verfügbar oder Sicherheitsstufe nicht ausreichend."
            )
            return None

    def get_sensor(self, name, secured_id_card: SecuredIdentityCard):
        sensor = self.sensors.get(name)
        if sensor and sensor.check_security(secured_id_card.security_level.name):
            return sensor
        else:
            print(
                f"Sensor {name} nicht verfügbar oder Sicherheitsstufe nicht ausreichend."
            )
            return None

    def get_all_activators(self, secured_id_card: SecuredIdentityCard):
        return [
            activator
            for activator in self.activators
            if isinstance(activator, Tool)
            and activator.check_security(secured_id_card.security_level)
        ]

    def get_all_sensors(self, secured_id_card: SecuredIdentityCard):
        return [
            sensor
            for sensor in self.sensors
            if isinstance(sensor, Tool)
            and sensor.check_security(secured_id_card.security_level.name)
        ]

    def get_all_tools(self, secured_id_card: SecuredIdentityCard):
        return self.get_all_activators(secured_id_card) + self.get_all_sensors(
            secured_id_card
        )
