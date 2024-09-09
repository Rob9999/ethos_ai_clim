import torch
import torch.nn as nn

from ethos_ai.util.translate import Translations


class EthicsModule(nn.Module):
    def __init__(self, domains):
        super(EthicsModule, self).__init__()
        self.domains = domains
        self.aggregator = nn.Sequential(
            nn.Linear(len(domains), 64), nn.ReLU(), nn.Linear(64, 1)
        )

    def forward(self, gpt_output, original_input):
        domain_scores = []
        domain_ethic_values = []
        for domain in self.domains:
            ethic_value = domain.evaluate(gpt_output)
            domain_ethic_values.append(ethic_value)
            domain_scores.append(torch.tensor(ethic_value))

        domain_scores = torch.stack(domain_scores).unsqueeze(0)
        overall_score = self.aggregator(domain_scores)
        overall_ethic_value = sum(domain_ethic_values)

        decision = "GO" if overall_ethic_value > 0 else "NO GO"
        summary_reason = self.generate_summary(domain_ethic_values, decision)

        return domain_ethic_values, overall_ethic_value, decision, summary_reason

    def generate_summary(self, domain_ethic_values, decision):
        key_points = []
        for i, value in enumerate(domain_ethic_values):
            if value < 0:
                key_points.append(
                    Translations.translate(
                        "DOMAIN_SUPPORTIVE_VALUE_OF", i + 1, self.domains[i].name, value
                    )
                )

            else:
                key_points.append(
                    Translations.translate(
                        "DOMAIN_CRTIICAL_VALUE_OF", i + 1, self.domains[i].name, value
                    )
                )
        summary = f"\nDecision: {decision}.\n" + "\n".join(key_points)
        return summary
