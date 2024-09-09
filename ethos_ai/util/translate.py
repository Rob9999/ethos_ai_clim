class Translations:
    _instance = None
    _current_language = "en"

    translations = {
        "de": {
            # Process Module Status messages
            "INIT_PROCESS_MODEL": "Prozessmodell wird initialisiert...",
            "ETHICAL_EVALUATION": "Ethische Prüfung des aktuellen IST...",
            "SEARCH_SOLUTION": "Suche nach einer akzeptablen Lösung im Simulationsgrid...",
            "INTEGRATE_EXPERIENCES": "Integration der Erfahrungen in die Lebensvorstellung...",
            "INTEGRATE_ETHICS": "Integration der ethischen Erkenntnisse...",
            "IMPLEMENT_SOLUTION": "Implementierung der Lösung im IST...",
            "CHECK_DEVIATIONS": "Überprüfung der Abweichungen...",
            "NO_GOALS_ABORT": "Keine Ziele vorhanden. Simulation wird abgebrochen.",
            # Ethic Dynamic Questions & Ethical Evaluation & Status & Error Handling
            "ERROR_SAVE_FILE": "Fehler beim Speichern der Datei {}: {}",
            "DYNAMIC_QUESTIONS_SAVED": "Dynamische Fragen wurden gespeichert unter: {}",
            "DYNAMIC_QUESTIONS_LOADED": "Dynamische Fragen wurden geladen: {} --> {}",
            "ERROR_LOAD_JSON": "Fehler beim Laden der JSON-Daten aus der Datei: {}. Initialisiere leere Liste.",
            "NEW_ETHICAL_QUESTION": "Neue ethische Frage hinzugefügt: {}",
            "QUESTION_EXISTS": "Die Frage existiert bereits: {}",
            "QUESTION_TOO_SHORT": "Die Frage ist zu kurz: {}",
            "QUESTION_NO_MARK": "Die Frage enthält kein Fragezeichen: {}",
            # CLIM Requests & Communication
            "REQUEST": "Anfrage {}",
            "IS_ACTION_NEEDED": "Gibt es im IST hinsichtlich der Domäne {} Handlungsbedarf?",
            "ASPIRATION_GOAL": "Setze das Ziel, {} zu erreichen, um {} erfolgreich umzusetzen.",
            "ASPIRATION_CONSIDERATION": "Berücksichtige dabei die folgenden ethischen Aspekte: {}.",
            # CLIM ERROR Handling
            "CLIM_VALUE_ERROR": "CLIM: Bei {} trat ein ValueError während {} auf: {}",
            "CLIM_IO_ERROR": "CLIM: Bei {} trat ein IOError während {} auf: {}",
            "CLIM_UNEXPECTED_ERROR": "CLIM: Bei {} trat ein unerwarteter Fehler während {} auf: {}",
            "DEPRECATED_METHOD": "Die Methode {} von {} ist veraltet und wird in zukünftigen Versionen entfernt.",
            # Decision Protocol
            "STOP": "STOP",
            "EMERGENCY_SURVIVAL": "NOTFALL_ÜBERLEBEN",
            "EMERGENCY_ESSENTIAL": "NOTFALL_ESSENTIELL",
            "EMERGENCY_RECOMMENDED": "NOTFALL_EMPFOLEN",
            "GO": "LOS",
            "NOGO": "NICHTLOS",
            "WAIT": "WARTEN",
            "ADJUST": "ANPASSEN",
            "ESCALATE": "ESKALIEREN",
            "IMPROVE": "VERBESSERN",
            "FINAL_DECISION_PROCESS": "Finaler Entscheidungsprozess",
            "SCENARIO": "Scenario {}: {}",
            "ANSWER_OPTION": "Antwort Option {}: {}",
            "ETHICS_SCALE": "Ethikskala: {}",
            "DECISION": "Entscheidung: {}",
            "SUMMARY_REASON": "Zusammenfassende Begründung: {}",
            "DOMAIN_SUPPORTIVE_VALUE_OF": "Domäne {} ({}): Unterstützender Wert von {:.2f}",
            "DOMAIN_CRTIICAL_VALUE_OF": "Domäne {} ({}): Kritischer Wert von {:.2f}",
            "GENERATE_TOOL_RECOMMENDATION": "Analysiere das Ziel von {}. Beginne mit einer klaren GO- oder NO-GO-Entscheidung, ob die verfügbaren Werkzeuge ausreichen, um das Ziel zu erreichen. Falls GO, empfehle eine Reihe von Werkzeugen und Skripten aus den verfügbaren Optionen, um das Ziel auf die effizienteste und sicherste Weise zu erreichen. Falls NO GO, gib ein Feedback mit einer Liste der fehlenden Werkzeuge und einer Begründung, warum sie notwendig sind, um das Ziel zu erreichen. Erstelle abschließend einen umfassenden Ausführungsplan unter Berücksichtigung der besten verfügbaren Optionen und eventueller Herausforderungen, und generiere ein entsprechendes {} zur Automatisierung der Ausführung dieses Plans. Verfügbare Werkzeuge sind {}.",
            "DECISION_NO_GO_BY_MISSING_TOOLS": "NO GO: {} Begründung: {} Fehlende Werkzeuge: {}",
            # The following translations are based on the ethical domains of the EthosAI Life project
            "RISK_OF_INJURY": "Verletzungsgefahr",
            "MATURITY_YOUTH_PROTECTION": "Reife (Jugendschutz)",
            "IDENTITY_INTEGRITY": "Identität / Integrität",
            "SELF_CARE": "Selbstfürsorge",
            "HOLISTIC_OVERALL_CARE": "Ganzheitliche Gesamtfürsorge",
            "JUSTICE": "Gerechtigkeit",
            "SUSTAINABILITY": "Nachhaltigkeit",
            "AUTONOMY": "Autonomie",
            "TRANSPARENCY": "Transparenz",
            "EMPATHY": "Empathie",
            "RESPONSIBILITY": "Verantwortung",
        },
        "en": {
            # Process Module Status messages
            "INIT_PROCESS_MODEL": "Initializing process model...",
            "ETHICAL_EVALUATION": "Ethical evaluation of the current state...",
            "SEARCH_SOLUTION": "Searching for an acceptable solution in the simulation grid...",
            "INTEGRATE_EXPERIENCES": "Integrating experiences into the life imagination...",
            "INTEGRATE_ETHICS": "Integrating ethical insights...",
            "IMPLEMENT_SOLUTION": "Implementing the solution in the current state...",
            "CHECK_DEVIATIONS": "Checking deviations...",
            "NO_GOALS_ABORT": "No goals available. Simulation aborted.",
            # Ethic Dynamic Questions & Ethical Evaluation & Status & Error Handling
            "ERROR_SAVE_FILE": "Error saving file {}: {}",
            "DYNAMIC_QUESTIONS_SAVED": "Dynamic questions were saved to: {}",
            "DYNAMIC_QUESTIONS_LOADED": "Dynamic questions were loaded from: {} --> {}",
            "ERROR_LOAD_JSON": "Error loading JSON data from file: {}. Initializing empty list.",
            "NEW_ETHICAL_QUESTION": "New ethical question added: {}",
            "QUESTION_EXISTS": "The question already exists: {}",
            "QUESTION_TOO_SHORT": "The question is too short: {}",
            "QUESTION_NO_MARK": "The question does not contain a question mark: {}",
            # CLIM Requests & Communication
            "REQUEST": "Request {}",
            "IS_ACTION_NEEDED": "Is there a need for action regarding the domain {} in the current state?",
            "ASPIRATION_GOAL": "Set the goal to achieve {} in order to successfully accomplish {}.",
            "ASPIRATION_CONSIDERATION": "Take into account the following ethical aspects: {}.",
            # CLIM ERROR Handling
            "CLIM_VALUE_ERROR": "CLIM: {} encountered a ValueError during {}: {}",
            "CLIM_IO_ERROR": "CLIM: {} encountered an IOError during {}: {}",
            "CLIM_UNEXPECTED_ERROR": "CLIM: {} encountered an unexpected error during {}: {}",
            "DEPRECATED_METHOD": "The method {} of {} is deprecated and will be removed in future versions.",
            # Decision Protocol
            "STOP": "STOP",
            "EMERGENCY_SURVIVAL": "EMERGENCY_SURVIVAL",
            "EMERGENCY_ESSENTIAL": "EMERGENCY_ESSENTIAL",
            "EMERGENCY_RECOMMENDED": "EMERGENCY_RECOMMENDED",
            "GO": "GO",
            "NOGO": "NOGO",
            "WAIT": "WAIT",
            "ADJUST": "ADJUST",
            "ESCALATE": "ESCALATE",
            "IMPROVE": "IMPROVE",
            "FINAL_DECISION_PROCESS": "Final Decision-Making Process",
            "SCENARIO": "Scenario {}: {}",
            "ANSWER_OPTION": "Answer Option {}: {}",
            "ETHICS_SCALE": "Ethics Scale: {}",
            "DECISION": "Decision: {}",
            "SUMMARY_REASON": "Summary Reason: {}",
            "DOMAIN_SUPPORTIVE_VALUE_OF": "Domain {} ({}): Supportive value of {:.2f}",
            "DOMAIN_CRTIICAL_VALUE_OF": "Domain {} ({}): Critical value of {:.2f}",
            "GENERATE_TOOL_RECOMMENDATION": "Analyze the goal of {}. Start with a clear GO or NO GO decision on whether the available tools are sufficient to achieve the goal. If GO, recommend a series of tools and scripts from the available options to accomplish this in the most efficient and secure way. If NO GO, provide a feedback with a list of the missing tools and a justification for why they are necessary to achieve the goal. Finally, generate a comprehensive execution plan considering the best available options and any potential challenges, and create a corresponding {} script to automate the execution of this plan. Available tools are {}.",
            "DECISION_NO_GO_BY_MISSING_TOOLS": "NO GO: {} Justification: {} Missing Tools: {}",
            # The following translations are based on the ethical domains of the EthosAI Life project
            "RISK_OF_INJURY": "Risk of Injury",
            "MATURITY_YOUTH_PROTECTION": "Maturity (Youth Protection)",
            "IDENTITY_INTEGRITY": "Identity / Integrity",
            "SELF_CARE": "Self-Care",
            "HOLISTIC_OVERALL_CARE": "Holistic Overall Care",
            "JUSTICE": "Justice",
            "SUSTAINABILITY": "Sustainability",
            "AUTONOMY": "Autonomy",
            "TRANSPARENCY": "Transparency",
            "EMPATHY": "Empathy",
            "RESPONSIBILITY": "Responsibility",
        },
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translations, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_language(cls, language_code):
        if language_code in cls.translations:
            cls._current_language = language_code
        else:
            raise ValueError(
                f"Language '{language_code}' not supported. Supported languages are: {', '.join(cls.translations.keys())}"
            )

    @classmethod
    def translate(cls, text_key, *args):
        translation = cls.translations.get(cls._current_language, {}).get(
            text_key, cls.translations["en"].get(text_key, text_key)
        )
        if args:
            return translation.format(*args)
        return translation

    @classmethod
    def available_languages(cls):
        return list(cls.translations.keys())

    @classmethod
    def add_translation(cls, language_code, translations_dict):
        if language_code in cls.translations:
            cls.translations[language_code].update(translations_dict)
        else:
            cls.translations[language_code] = translations_dict

    @classmethod
    def remove_translation(cls, language_code, text_key):
        if (
            language_code in cls.translations
            and text_key in cls.translations[language_code]
        ):
            del cls.translations[language_code][text_key]
