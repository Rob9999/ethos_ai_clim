from ethos_ai.clim.base_clim import BaseCLIM

"""
LTCLIM class represents a Long Term Current Life Imagination Model for the EthosAI Life application.
Attributes:
    identity (SecuredIdentityCard): The secured identity card of the user.
    password (str): The password of the user.
    tool_manager (ToolManager): The tool manager instance.
Methods:
    __init__(identity: SecuredIdentityCard, password: str, tool_manager: ToolManager):
        Initializes a new instance of the LTCLIM class.
"""
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.tool.tool_manager import ToolManager


class LTCLIM(BaseCLIM):

    def __init__(
        self, identity: SecuredIdentityCard, password: str, tool_manager: ToolManager
    ):
        super().__init__(
            name="LTCLIM",
            identity=identity,
            tool_manager=tool_manager,
        )
