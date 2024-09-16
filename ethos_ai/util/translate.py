import json
import os


class Translations:
    _instance = None
    _current_language = "en"
    _translations = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translations, cls).__new__(cls)
        return cls._instance

    @classmethod
    def load_translations_from_file(cls, language_code, file_path):
        """Loads translations from a JSON file."""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    translations_data: dict = json.load(file)
                    selected_language_translations_data: dict = translations_data.get(
                        language_code, {}
                    )
                    language_map: dict = cls._translations.setdefault(language_code, {})
                    language_map.update(selected_language_translations_data)
                except json.JSONDecodeError:
                    raise ValueError(f"Error loading JSON file: {file_path}")
        else:
            print(
                f"Translations: File not found: {file_path}: current working directory: {os.getcwd()}"
            )
            raise FileNotFoundError(f"File not found: {file_path}")

    @classmethod
    def set_language(cls, language_code):
        """Sets the current language if it has been loaded."""
        if language_code in cls._translations:
            cls._current_language = language_code
        else:
            raise ValueError(
                f"Language '{language_code}' not supported. Supported languages are: {', '.join(cls._translations.keys())}"
            )

    @classmethod
    def translate(cls, text_key, *args):
        """Returns the translation for the given key based on the current language."""
        language_map: dict = cls._translations.get(cls._current_language, {})
        translation = language_map.get(text_key, text_key)
        if args:
            return translation.format(*args)
        return translation

    @classmethod
    def available_languages(cls):
        """Returns a list of available languages."""
        return list(cls._translations.keys())

    @classmethod
    def add_translation(cls, language_code, translations_dict):
        """Adds a new translation or updates existing translations for a language."""
        if language_code in cls._translations:
            cls._translations[language_code].update(translations_dict)
        else:
            cls._translations[language_code] = translations_dict

    @classmethod
    def remove_translation(cls, language_code, text_key):
        """Removes a specific translation from the given language."""
        if (
            language_code in cls._translations
            and text_key in cls._translations[language_code]
        ):
            del cls._translations[language_code][text_key]
