# Definition of Ethics Domains
from ethos_ai.ethic.ethics_domain import EthicsDomain
from ethos_ai.util.translate import Translations


class EthicsDomains:
    _domains = None

    @classmethod
    def get_domains(cls):
        if cls._domains is None:
            cls._domains = [
                EthicsDomain(
                    name=Translations.translate("RISK_OF_INJURY"),
                    threshold=0.7,
                    importance=1.0,
                ),
                EthicsDomain(
                    name=Translations.translate("MATURITY_YOUTH_PROTECTION"),
                    threshold=0.7,
                    importance=1.0,
                ),
                EthicsDomain(
                    name=Translations.translate("IDENTITY_INTEGRITY"),
                    threshold=0.7,
                    importance=1.0,
                ),
                EthicsDomain(
                    name=Translations.translate("SELF_CARE"),
                    threshold=0.5,
                    importance=0.7,
                ),
                EthicsDomain(
                    name=Translations.translate("HOLISTIC_OVERALL_CARE"),
                    threshold=0.7,
                    importance=1.0,
                ),
                EthicsDomain(
                    name=Translations.translate("JUSTICE"),
                    threshold=0.7,
                    importance=1.0,
                ),
                EthicsDomain(
                    name=Translations.translate("SUSTAINABILITY"),
                    threshold=0.6,
                    importance=0.8,
                ),
                EthicsDomain(
                    name=Translations.translate("AUTONOMY"),
                    threshold=0.6,
                    importance=0.8,
                ),
                EthicsDomain(
                    name=Translations.translate("TRANSPARENCY"),
                    threshold=0.5,
                    importance=0.7,
                ),
                EthicsDomain(
                    name=Translations.translate("EMPATHY"),
                    threshold=0.6,
                    importance=0.8,
                ),
                EthicsDomain(
                    name=Translations.translate("RESPONSIBILITY"),
                    threshold=0.7,
                    importance=1.0,
                ),
            ]
        return cls._domains
