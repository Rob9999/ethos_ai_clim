import argparse
from ethos_ai.util.translate import Translations
from ethos_ai.ethos_ai_individual import EthosAIIndividual


def main():
    parser = argparse.ArgumentParser(description="Start EthosAI Life Individual")
    # Hier können weitere Argumente hinzugefügt werden
    args = parser.parse_args()

    Translations.set_language("en")

    ethos_ai_individual = EthosAIIndividual()
    ethos_ai_individual.start()


if __name__ == "__main__":
    main()
