import torch
import torch.nn as nn

from ethos_ai.clim.base_clim import BaseCLIM
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.tool.tool_manager import ToolManager


# Short And Medium Term CLIM
# This class is responsible for the training of the Short and Medium Term CLIM model.
# Deutsch: Kurz- und Mittelfristiges CLIM (vergl. Kurz- und Mittelfrist Gedächtnis im Gegensatz zu Langfristgedächtnis das durch CLIM repräsentiert wird durch GPT-2 oder höher)
class SAMTCLIM(BaseCLIM):

    def __init__(
        self, identity: SecuredIdentityCard, password: str, tool_manager: ToolManager
    ):
        super().__init__(
            name="SAMT",
            identity=identity,
            tool_manager=tool_manager,
        )
