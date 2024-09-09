from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.security.exception.security_access_exception import (
    SecurityAccessException,
)


class BaseIndividual:
    def __init__(self, secured_identity_card: SecuredIdentityCard):
        if isinstance(secured_identity_card, SecuredIdentityCard):
            self.secured_identity_card = secured_identity_card
        else:
            raise SecurityAccessException(
                "Fehler beim Erstellen des Individuums: Die Identitätskarte ist nicht sicher."
            )

    def get_name(self):
        return self.secured_identity_card.name

    def get_security_level(self):
        return self.secured_identity_card.security_level

    def get_id(self):
        return self.secured_identity_card

    def get_public_key(self):
        return self.secured_identity_card.public_key

    def encode_message(self, message: str) -> bytes:
        return self.secured_identity_card.encrypt_message(message)

    def decode_message(self, code: bytes) -> str:
        return self.secured_identity_card.decrypt_message(code)

    def sign_message(self, message: str) -> bytes:
        return self.secured_identity_card.sign_message(message)

    def verify_signature(self, encrypted_message: bytes) -> bool:
        return self.secured_identity_card.verify_signature_without_decrypting(
            encrypted_message
        )
