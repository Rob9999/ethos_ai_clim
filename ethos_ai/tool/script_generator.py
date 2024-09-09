from ethos_ai.clim.clim_interface import CLIMInterface
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.tool.tool_manager import ToolManager
from ethos_ai.topic.to_do_topic import ToDoTopic
from ethos_ai.util.protocol import Protocol
from ethos_ai.util.translate import Translations


class ScriptGenerator:

    __name__ = "ScriptGenerator"
    protocol = Protocol()

    @staticmethod
    def generate_script(
        clim: CLIMInterface,
        tool_manager: ToolManager,
        todo_topic: ToDoTopic,
        secured_id_card: SecuredIdentityCard = None,
        script_language: str = "python",
    ) -> tuple[str, str, str, list, str]:
        # get available tools using passed secured_id_card, if not available use protocol.identity
        available_tools = tool_manager.get_all_tools(
            secured_id_card if secured_id_card else ScriptGenerator.protocol.identity
        )
        description = todo_topic.description
        prompt = Translations.translate(
            "GENERATE_TOOL_RECOMMENDATION",
            description,
            script_language,
            available_tools,
        )
        output = clim.generate_text(prompt)
        # parse GO/NO GO decision
        decision = output.split(":")[0].strip()
        if decision == "GO":
            # extract tools and scripts
            tools_and_scripts = output.split(":")[1].strip()
            tools = tools_and_scripts.split(", ")
            scripts = tools_and_scripts.split(", ")
            # create execution plan
            execution_plan = f"Execution Plan for ToDoTopic: {todo_topic.description}\n"
            for tool in tools:
                execution_plan += f"Use tool: {tool}\n"
            for script in scripts:
                execution_plan += f"Execute script: {script}\n"
            # create script
            script_content = ScriptGenerator.make_to_comment(
                f"Script for ToDoTopic:\n=====================\n{todo_topic.description}\n",
                script_language=script_language,
            )
            script_content += ScriptGenerator.make_to_comment(
                f"Aspiration:\n===========\n{todo_topic.aspiration}\n",
                script_language=script_language,
            )
            for tool in tools:
                script_content += f"activate_tool('{tool}')\n"
            for script in scripts:
                script_content += f"execute_script('{script}')\n"
            script_content += "print('Instruction Script completed.')"
            return "GO", script_content, execution_plan, tools, None
        else:
            missing_tools = output.split(":")[1].strip()
            justification = output.split(":")[2].strip()
            return "NO GO", None, None, missing_tools, justification

    @staticmethod
    def make_to_comment(text: str, script_language: str) -> str:
        lines = text.split("\n")
        if script_language == "python":
            return "\n".join([f"# {line}" for line in lines if line.strip() != ""])
        elif script_language in ["javascript", "typescript"]:
            return "\n".join([f"// {line}" for line in lines if line.strip() != ""])
        else:
            ScriptGenerator.protocol.warning("Ungültige Skriptsprache.")
            return ""  # fall back to empty string
