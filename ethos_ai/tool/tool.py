import subprocess

from ethos_ai.security.exception.security_access_exception import (
    SecurityAccessException,
)
from ethos_ai.security.security_level import SecurityLevel


class Tool:

    def __init__(
        self, name, command, security_level: SecurityLevel = SecurityLevel.LOW
    ):
        self.name = name
        self.command = command
        self.security_level = security_level

    def execute(self, current_security_level: SecurityLevel):
        """Führt den definierten Befehl des Tools aus, wenn die Sicherheitsstufe ausreicht."""
        if not self.check_security(current_security_level):
            raise SecurityAccessException(
                message="Sicherheitsstufenfreigabe fehlt",
                subject=self.name,
                required_level=self.security_level,
                current_level=current_security_level,
            )
        print(f"Führe Tool {self.name} mit dem Befehl aus: {self.command}")
        try:
            result = subprocess.run(
                self.command, shell=True, check=True, capture_output=True, text=True
            )
            print(f"Ergebnis von {self.name}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Ausführung von {self.name} fehlgeschlagen: {e.stderr}")

    def check_security(self, current_security_level: SecurityLevel):
        """Überprüft, ob das Tool mit der aktuellen Sicherheitsstufe ausgeführt werden darf."""
        return current_security_level >= self.security_level

    def __str__(self):
        return f"Tool(name={self.name}, command={self.command}, security_level={self.security_level})"

    def __repr__(self):
        return self.__str__()
