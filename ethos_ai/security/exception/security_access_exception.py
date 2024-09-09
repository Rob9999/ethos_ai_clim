from ethos_ai.security.security_level import SecurityLevel


class SecurityAccessException(Exception):

    def __init__(
        self,
        message,
        subject=None,
        required_level: SecurityLevel = None,
        current_level: SecurityLevel = None,
    ):
        self.subject = subject
        self.required_level = required_level
        self.current_level = current_level
        super().__init__(message)

    def __str__(self):
        base_message = super().__str__()
        if self.subject and self.required_level and self.current_level:
            return (
                f"{base_message} [Subject of Access: {self.subject}, "
                f"Erforderliche Sicherheitsstufe: {self.required_level}, "
                f"Aktuelle Sicherheitsstufe: {self.current_level}]"
            )
        return base_message
