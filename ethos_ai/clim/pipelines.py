from ethos_ai.clim.decision import Decision
from ethos_ai.clim.ethic_clim import EthicCLIM
from ethos_ai.clim.individual_clim import IndividualCLIM
from ethos_ai.clim.ltclim import LTCLIM
from ethos_ai.clim.samt_clim import SAMTCLIM


class Pipelines:
    @staticmethod
    def standard_pipeline(
        ethic: EthicCLIM, individual: IndividualCLIM, samt: SAMTCLIM, lclim: LTCLIM
    ):
        return [
            ("prerun", ethic),  # Ethikvorprüfung
            ("prerun", individual),  # Individuelle Voranpassung
            ("prerun", samt),  # Kurz- und mittelfristige Voroptimierung
            ("all", lclim),  # Langfristige Analyse (komplexes All-Modell)
            ("final", samt),  # Finale Kurz- und mittelfristige Optimierung
            ("final", individual),  # Finale individuelle Anpassung
            ("final", ethic),  # Finale Ethikprüfung
        ]

    @staticmethod
    def emergency_survival_pipeline(ethic: EthicCLIM, samt: SAMTCLIM):
        return [
            (Decision.EMERGENCY_SURVIVAL.name, ethic),
            (Decision.EMERGENCY_SURVIVAL.name, samt),
        ]

    @staticmethod
    def emergency_essential_pipeline(
        ethic: EthicCLIM, samt: SAMTCLIM, individual: IndividualCLIM
    ):
        return [
            (Decision.EMERGENCY_ESSENTIAL.name, ethic),
            (Decision.EMERGENCY_ESSENTIAL.name, samt),
            (Decision.EMERGENCY_ESSENTIAL.name, individual),
        ]

    @staticmethod
    def emergency_recommended_pipeline(samt: SAMTCLIM, individual: IndividualCLIM):
        return [
            (Decision.EMERGENCY_RECOMMENDED.name, samt),
            (Decision.EMERGENCY_RECOMMENDED.name, individual),
        ]
