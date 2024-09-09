import datetime
from email import utils
import bcrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

import os

from enum import Enum

from ethos_ai.security.exception.security_access_exception import (
    SecurityAccessException,
)
from ethos_ai.security.security_level import SecurityLevel


class SecuredIdentityCard:
    def __init__(
        self,
        name,
        password,
        security_level: SecurityLevel,
        responsible=None,
        key_dir="keys",
    ):
        self.name = name
        self.security_level = security_level
        self.responsible = (
            responsible  # Kann ein spezifischer Advisor oder ein EthosAIIndividual sein
        )
        self.public_key = None
        self.private_key_path = os.path.join(key_dir, f"{self.name}_private_key.pem")
        self.public_key_path = os.path.join(key_dir, f"{self.name}_public_key.pem")

        if not os.path.exists(self.private_key_path) or not os.path.exists(
            self.public_key_path
        ):
            self.generate_keys(key_dir)
        else:
            self.load_keys()

        # Passwort hashen und speichern
        self.password_hash = self.hash_password(password)

    def hash_password(self, password):
        """Hasht ein Passwort mit bcrypt und speichert den Hash."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def verify_password(self, input_password):
        """Überprüft, ob das eingegebene Passwort mit dem gespeicherten Hash übereinstimmt."""
        return bcrypt.checkpw(input_password.encode("utf-8"), self.password_hash)

    def generate_keys(self, key_dir):
        """Generiert ein neues RSA-Schlüsselpaar und speichert es im Dateisystem."""
        # Sicherstellen, dass das Verzeichnis existiert
        os.makedirs(key_dir, exist_ok=True)

        # Generiere den privaten Schlüssel
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        # Speichere den privaten Schlüssel im PEM-Format
        with open(self.private_key_path, "wb") as private_key_file:
            private_key_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # Generiere den öffentlichen Schlüssel
        public_key = private_key.public_key()

        # Speichere den öffentlichen Schlüssel im PEM-Format
        with open(self.public_key_path, "wb") as public_key_file:
            public_key_file.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

        self.public_key = public_key

    def load_keys(self):
        """Lädt den privaten und öffentlichen Schlüssel von der Festplatte."""
        # Lade den privaten Schlüssel
        with open(self.private_key_path, "rb") as private_key_file:
            self.private_key = serialization.load_pem_private_key(
                private_key_file.read(), password=None, backend=default_backend()
            )

        # Lade den öffentlichen Schlüssel
        with open(self.public_key_path, "rb") as public_key_file:
            self.public_key = serialization.load_pem_public_key(
                public_key_file.read(), backend=default_backend()
            )

    def encrypt_message(self, message: str) -> bytes:
        """Verschlüsselt eine Nachricht mit dem öffentlichen Schlüssel."""
        return self.public_key.encrypt(
            message.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def decrypt_message(self, encrypted_message: bytes) -> str:
        """Entschlüsselt eine Nachricht mit dem privaten Schlüssel."""
        return self.private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        ).decode("utf-8")

    def verify_public_key(self, public_key: str = None):
        """Überprüft, ob der spezifizierte public key (oder falls None, der gespeicherte öffentliche Schlüssel) mit dem privaten Schlüssel übereinstimmt."""
        # Testnachricht
        test_message = "verify_public_key_test"
        encrypted_message = self.encrypt_message(test_message)
        decrypted_message = self.decrypt_message(encrypted_message)

        if decrypted_message != test_message:
            raise SecurityAccessException(
                message="Öffentlicher Schlüssel stimmt nicht mit privatem Schlüssel überein",
                subject=None,
                required_level=None,
                current_level=self.security_level.name,
            )

    def try_verify_public_key(self, public_key: str = None):
        """Versucht, den spezifizierten public key (oder falls None, den gespeicherten öffentlichen Schlüssel) zu überprüfen, gibt True zurück, wenn erfolgreich."""
        try:
            self.verify_public_key()
            return True
        except SecurityAccessException as e:
            print(f"Sicherheitsausnahme: {e}")
            return False

    def check_security(self, required_level: SecurityLevel, input_password):
        """Überprüft, ob die Sicherheitsstufe ausreicht und ob das Passwort korrekt ist."""
        if not self.verify_password(input_password):
            raise SecurityAccessException(
                message="Ungültiges Passwort",
                subject=None,
                required_level=required_level.name,
                current_level=self.security_level.name,
            )
        if self.security_level.value < required_level.value:
            raise SecurityAccessException(
                message="Sicherheitsstufenfreigabe fehlt",
                subject=None,
                required_level=required_level.name,
                current_level=self.security_level.name,
            )

    def try_check_security(self, required_level: SecurityLevel, input_password):
        """Versucht, die Sicherheitsstufe zu überprüfen, gibt True zurück, wenn erfolgreich."""
        try:
            self.check_security(required_level, input_password)
            return True
        except SecurityAccessException as e:
            print(f"Sicherheitsausnahme: {e}")
            return False

    def sign_message(self, message: str) -> bytes:
        """Signiert eine Nachricht, fügt Ort, Datum und Unterschrift hinzu und verschlüsselt sie."""
        location = "Some Location"
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        signature_info = f"Signed by {self.name}"
        message_with_metadata = f"{message}\n\nLocation: {location}\nDate: {date}\nSignature Info: {signature_info}"
        # Nachricht hashen
        message_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        message_hash.update(message_with_metadata.encode("utf-8"))
        digest = message_hash.finalize()
        # Nachricht signieren
        signature = self.private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256()),
        )
        # Signatur an die Nachricht anhängen
        signed_message = (
            message_with_metadata.encode("utf-8") + b"\nSignature: " + signature
        )
        # Verschlüsseln der signierten Nachricht
        encrypted_message = self.encrypt_message(signed_message.decode("utf-8"))
        return encrypted_message

    def decrypt_and_verify_message(self, encrypted_message: bytes) -> str:
        """Entschlüsselt eine Nachricht, überprüft die Signatur und gibt den Inhalt zurück, falls gültig."""
        # Entschlüssele die Nachricht
        decrypted_message = self.decrypt_message(encrypted_message)

        # Trenne die Nachricht, die Metadaten und die Signatur
        try:
            message_parts = decrypted_message.rsplit("\nSignature: ", 1)
            if len(message_parts) != 2:
                raise SecurityAccessException(
                    "Die Nachricht enthält keine gültige Signatur."
                )

            original_message = message_parts[0]
            signature = message_parts[1].encode("utf-8")

            # Nachricht hashen
            message_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
            message_hash.update(original_message.encode("utf-8"))
            digest = message_hash.finalize()

            # Überprüfe die Signatur
            self.public_key.verify(
                signature,
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                utils.Prehashed(hashes.SHA256()),
            )

            # Wenn die Überprüfung erfolgreich ist, gib die Nachricht zurück
            return original_message

        except InvalidSignature:
            raise SecurityAccessException(
                "Ungültige Signatur. Die Nachricht wurde möglicherweise manipuliert."
            )
        except Exception as e:
            raise SecurityAccessException(
                f"Fehler bei der Überprüfung der Nachricht: {e}"
            )

    def verify_signature_without_decrypting(self, encrypted_message: bytes) -> bool:
        """Versucht, die Signatur zu überprüfen, ohne die Nachricht zu entschlüsseln."""
        try:
            # Entschlüsseln und Überprüfen, ohne den Inhalt weiterzuverarbeiten
            self.decrypt_and_verify_message(encrypted_message)
            return True
        except SecurityAccessException:
            return False

    def __str__(self):
        return f"Sicherheitsausweis(Name={self.name}, Sicherheitsstufe={self.security_level.name}, Verantwortlicher={self.responsible})"

    def __repr__(self):
        return self.__str__()
