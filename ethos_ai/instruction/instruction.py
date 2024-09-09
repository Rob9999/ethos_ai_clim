import subprocess
from ethos_ai.clim.clim_interface import CLIMInterface
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.tool.script_generator import ScriptGenerator
from ethos_ai.tool.tool_manager import ToolManager
from ethos_ai.topic.to_do_topic import ToDoTopic


class Instruction:

    def promote_to_instruction(
        clim: CLIMInterface,
        tool_manager: ToolManager,
        topic: ToDoTopic,
        secured_id_card: SecuredIdentityCard,
        script_language="python",
    ) -> "Instruction":
        if not topic.isReadyForIST:
            raise Exception("Das ToDoTopic ist nicht bereit für die Umsetzung im IST.")
        instruction = Instruction(
            clim=clim,
            tool_manager=tool_manager,
            todo_topic=topic,
            secured_id_card=secured_id_card,
            script_language=script_language,
        )
        return instruction

    def __init__(
        self,
        clim: CLIMInterface,
        tool_manager: ToolManager,
        todo_topic: ToDoTopic,
        secured_id_card: SecuredIdentityCard,
        script_language="python",
    ):
        self.todo_topic = todo_topic
        if not todo_topic.parameters or not todo_topic.parameters.get("script"):
            self.script = ScriptGenerator.generate_script(
                clim=clim,
                tool_manager=tool_manager,
                todo_topic=todo_topic,
                secured_id_card=secured_id_card,
                script_language=script_language,
            )
            self.script_language = script_language if self.script else None
        else:
            self.script = todo_topic.parameters.get("script")
            self.script_language = todo_topic.parameters.get(
                "script_language", "javascript"
            )

    def execute(self):
        """Führt das generierte Skript zur Laufzeit aus."""
        if self.script_language == "python":
            exec(self.script)  # Führt das generierte Python-Skript aus
        elif self.script_language in ["javascript", "typescript"]:
            # Beispielhafte Ausführung für JavaScript/TypeScript (Voraussetzung: node.js installiert)
            try:
                with open("temp_script.js", "w") as script_file:
                    script_file.write(self.script)
                subprocess.run("node temp_script.js", shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Fehler bei der Ausführung des Skripts: {e.stderr}")
            finally:
                subprocess.run(
                    "rm temp_script.js", shell=True
                )  # Temporäre Datei löschen

    def save_script_to_file(self, filename):
        """Speichert das generierte Skript in einer Datei."""
        with open(filename, "w") as file:
            file.write(self.script)
        print(f"Skript wurde gespeichert unter: {filename}")

    def __str__(self):
        return self.script

    def __repr__(self):
        return f"Instruction(todo_topic={self.todo_topic.description}, script_language={self.script_language})"
