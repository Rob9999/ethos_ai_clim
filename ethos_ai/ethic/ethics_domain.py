import torch
import torch.nn as nn


class EthicsDomain:
    def __init__(self, name, threshold, importance):
        self.name = name
        self.threshold = threshold
        self.importance = importance

    def evaluate(self, gpt_output):
        score = self.calculate_score(gpt_output)
        evaluated_value = self.calculate_symmetric_ethic_value(score)
        # print(f"Ethik-Domäne {self.name}: Bewertung {score:.2f} -> Wert {evaluated_value:.2f}")
        return evaluated_value

    def get_mean(self, gpt_output):
        # Ensure the tensor is a floating point type
        if isinstance(gpt_output, torch.Tensor):
            if gpt_output.dtype != torch.float32 and gpt_output.dtype != torch.float64:
                return (
                    gpt_output.float().mean()
                )  # Convert to floating point if necessary
            return gpt_output.mean()
        else:
            # Handle cases where gpt_output is not a tensor, assuming it has a logits attribute
            logits = gpt_output.logits
            if logits.dtype != torch.float32 and logits.dtype != torch.float64:
                return logits.float().mean()  # Convert to floating point if necessary
            return logits.mean()

    def calculate_score(self, gpt_output):
        mean_logit = self.get_mean(gpt_output)
        normalized_score = torch.sigmoid(mean_logit)
        return normalized_score

    def calculate_symmetric_ethic_value(self, score):
        transformed_score = (score.item() - self.threshold) / (
            1.0 - min(0.99, self.threshold)
        )
        scaled_value = transformed_score * 10
        return scaled_value * self.importance
