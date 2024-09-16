import argparse
import os
from ethos_ai.util.translate import Translations
from ethos_ai.ethos_ai_individual import EthosAIIndividual


def main():
    parser = argparse.ArgumentParser(description="Start EthosAI Life Individual")
    # Hier können weitere Argumente hinzugefügt werden
    args = parser.parse_args()

    Translations.load_translations_from_file(
        "en", os.path.join("ethos_ai", "resources", "prompts", "prompts_en.json")
    )
    # Translations.load_translations_from_file("de", os.path.join("ethos_ai", "resources", "prompts", "prompts_de.json"))
    Translations.load_translations_from_file(
        "en", os.path.join("ethos_ai", "resources", "messages", "messages_en.json")
    )
    # Translations.load_translations_from_file("de", os.path.join("ethos_ai", "resources", "messages", "messages_de.json"))
    Translations.set_language("en")

    ethos_ai_individual = EthosAIIndividual()
    ethos_ai_individual.start()


if __name__ == "__main__":
    main()
