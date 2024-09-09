import json
import os
from ethos_ai.ethic.ethics_domains import EthicsDomains
from ethos_ai.util.protocol import Protocol
from ethos_ai.util.translate import Translations


class Ethics:

    def __init__(self, ethic_dir: str = "ethics", ethic_filename: str = "ethics.json"):
        self.protocol = Protocol()  # Create a protocol instance
        self.base_questions = self.load_base_questions()
        self.filepath = os.path.join(ethic_dir, ethic_filename)
        if os.path.exists(self.filepath):
            self.dynamic_questions = self.load_dynamic_questions(self.filepath)
        else:
            self.dynamic_questions = []

    def load_base_questions(self):
        base_questions = []
        for domain in EthicsDomains.get_domains():
            base_questions.append(
                Translations.translate("IS_ACTION_NEEDED", domain.name)
            )
        return base_questions

    def validate_question(self, question: str) -> bool:
        # Checks if the question is ethically relevant and reasonable
        if len(question) < 10:
            self.protocol.warning(
                Translations.translate("QUESTION_TOO_SHORT", question)
            )
            return False
        if "?" not in question:
            self.protocol.warning(Translations.translate("QUESTION_NO_MARK", question))
            return False
        return True

    def add_dynamic_question(self, question: str):
        if not self.validate_question(question):
            return

        if question not in self.dynamic_questions:
            self.dynamic_questions.append(question)
            self.protocol.info(Translations.translate("NEW_ETHICAL_QUESTION", question))
        else:
            self.protocol.warning(Translations.translate("QUESTION_EXISTS", question))

    def get_all_questions(self):
        return self.base_questions + self.dynamic_questions

    def _save_dynamic_questions(self, filepath: str):
        try:
            with open(filepath, "w") as file:
                json.dump(self.dynamic_questions, file, indent=4)
            self.protocol.info(
                Translations.translate("DYNAMIC_QUESTIONS_SAVED", filepath)
            )
        except IOError as e:
            self.protocol.error(
                Translations.translate("ERROR_SAVE_FILE", filepath, str(e))
            )

    def save_dynamic_questions(self):
        self._save_dynamic_questions(self.filepath)

    def _load_dynamic_questions(self, filepath):
        try:
            with open(filepath, "r") as file:
                dyn_quests = json.load(file)
                self.protocol.info(
                    Translations.translate(
                        "DYNAMIC_QUESTIONS_LOADED", filepath, dyn_quests
                    )
                )
                return dyn_quests
        except json.JSONDecodeError:
            self.protocol.error(Translations.translate("ERROR_LOAD_JSON", filepath))
            return []

    def load_dynamic_questions(self):
        return self._load_dynamic_questions(self.filepath)
