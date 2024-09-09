import subprocess
import json
import logging
from datetime import datetime

# Logging-Setup
logging.basicConfig(
    filename="./validate/tool_execution.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Laden der tools.json
with open("tools.json", "r") as file:
    tools_data = json.load(file)

# Laden der parameter.json
with open("./validate/parameter.json", "r") as file:
    parameter_data = json.load(file)


# Simulierte Funktion zur Ausführung von Shell-Befehlen mit erweiterter Fehlerbehandlung und Logging
def execute_command(command, tool_name):
    try:
        logging.info(f"Start executing: {tool_name} with command: {command}")
        print(f"************************************************************")
        print(f"Ausführen: {command}")
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = result.stdout.decode("utf-8")
        error_output = result.stderr.decode("utf-8")

        if output:
            print(
                f"\033[32mErgebnis:\n{output}\033[0m"
            )  # Grüne Ausgabe für erfolgreiche Ergebnisse
        if error_output:
            print(
                f"\033[31mFehlermeldung:\n{error_output}\033[0m"
            )  # Rote Ausgabe für Fehler

        print(f"************************************************************")
        logging.info(f"Ergebnis für {tool_name}:\n{output}")
        return output if result.returncode == 0 else None
    except subprocess.CalledProcessError as e:
        error_message = e.stderr
        print(
            f"\033[31mFehler beim Ausführen des Befehls: {e}\033[0m"
        )  # Rote Ausgabe für Fehler
        print(f"\033[31mFehlermeldung:\n{error_message}\033[0m")
        logging.error(f"Fehler beim Ausführen des Befehls {tool_name}: {error_message}")
        return None


def echo_error_message(tool_name, tool_command, error_message):
    echo_output = f"""
\033[31m*************************************************************************
\033[31m* FAILED:  {tool_command}
\033[31m* Message: {error_message}
\033[31m* (see more detail in the log)
\033[31m**************************************************************************
\033[0m"""
    print(
        f"\033[31mFehler beim Ausführen des Tools {tool_name}: {error_message}\033[0m"
    )
    logging.error(f"Fehler beim Ausführen des Tools {tool_name}: {error_message}")
    return echo_output


# Funktion zur Verarbeitung von Parametern
def process_parameters(
    tool_name: str, tool_command: str, tool_parameters, available_parameters
):
    print(f"Verarbeite Parameter für {tool_name}:")
    print(f"Ursprüngliches Kommando: {tool_command}")

    if tool_parameters is None:
        return True, tool_command, None

    if available_parameters is None:
        return (
            False,
            tool_command,
            echo_error_message(
                tool_name,
                tool_command,
                "No parameters are provided at all! Check parameter.json!",
            ),
        )

    if tool_name not in available_parameters:
        return (
            False,
            tool_command,
            echo_error_message(
                tool_name, tool_command, f"Missing parameters for {tool_name}"
            ),
        )

    provided_tool_parameters = available_parameters[tool_name]
    error = ""
    for key, value in provided_tool_parameters.items():
        tool_command = tool_command.replace(f"{{{key}}}", value)
    for key in tool_parameters:
        if tool_command.find(f"{{{key}}}") != -1:
            error += echo_error_message(
                tool_name, tool_command, f"Missing parameter: {key}"
            )

    print(f"Finales Kommando: {tool_command}")
    return error == "", tool_command, error


# Erweiterte Tests für Activators und Sensors mit Logging und Fehlerbehandlung
def test_tools(tools, available_parameters=None, tool_type="Activator"):
    print(f"\n--- Testen der {tool_type}s ---")
    for tool in tools:
        success, command, error = process_parameters(
            tool["name"], tool["command"], tool.get("parameter"), available_parameters
        )
        if success:
            output = execute_command(command, tool["name"])
            if output is not None:
                print(
                    f"\033[32m{tool_type} {tool['name']} erfolgreich ausgeführt.\033[0m\n\n"
                )
                logging.info(f"{tool_type} {tool['name']} erfolgreich ausgeführt.")
            else:
                print(
                    f"\033[31m{tool_type} {tool['name']} konnte nicht erfolgreich ausgeführt werden.\n\n\033[0m"
                )
                logging.warning(
                    f"{tool_type} {tool['name']} konnte nicht erfolgreich ausgeführt werden."
                )
        else:
            print(error)
            logging.error(error)


# Testen der Activators und Sensors
test_tools(tools_data["activators"], parameter_data, "Activator")
test_tools(tools_data["sensors"], parameter_data, "Sensor")

print("\n--- Test abgeschlossen. Ergebnisse im Log gespeichert. ---")
