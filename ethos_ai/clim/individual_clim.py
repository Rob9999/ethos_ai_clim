from ethos_ai.clim.base_clim import BaseCLIM
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.tool.tool_manager import ToolManager


class IndividualCLIM(BaseCLIM):
    def __init__(
        self, identity: SecuredIdentityCard, password: str, tool_manager: ToolManager
    ):
        super().__init__(
            name="Individual",
            identity=identity,
            tool_manager=tool_manager,
        )
