"""Encryption service — data-at-rest encryption using Fernet symmetric encryption.

Sprint 8 Story 5.7: Data Encryption
- Encrypt / decrypt arbitrary data
- Derive key from passphrase via PBKDF2
- Configurable salt stored alongside ciphertext
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Minimum passphrase requirements
_MIN_PASSPHRASE_LEN = 8
_PBKDF2_ITERATIONS = 100_000


def check_passphrase_strength(passphrase: str) -> dict[str, Any]:
    """Evaluate passphrase strength.

    Returns dict with keys: strong (bool), score (0-4), feedback (list[str]).
    """
    score = 0
    feedback: list[str] = []

    if len(passphrase) >= _MIN_PASSPHRASE_LEN:
        score += 1
    else:
        feedback.append(f"Must be at least {_MIN_PASSPHRASE_LEN} characters.")

    if re.search(r"[A-Z]", passphrase):
        score += 1
    else:
        feedback.append("Add at least one uppercase letter.")

    if re.search(r"[0-9]", passphrase):
        score += 1
    else:
        feedback.append("Add at least one digit.")

    if re.search(r"[^A-Za-z0-9]", passphrase):
        score += 1
    else:
        feedback.append("Add at least one special character.")

    return {
        "strong": score >= 3,
        "score": score,
        "feedback": feedback,
    }


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a Fernet key from a passphrase using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))


class EncryptionService:
    """Symmetric encryption for sensitive data at rest."""

    def __init__(self, passphrase: str) -> None:
        strength = check_passphrase_strength(passphrase)
        if not strength["strong"]:
            raise JarvisError(
                ErrorCode.PASSPHRASE_WEAK,
                detail="; ".join(strength["feedback"]),
            )
        self._passphrase = passphrase

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext and return base64 string (salt$ciphertext).

        Returns:
            String in format: base64(salt)$base64(ciphertext)
        """
        try:
            salt = os.urandom(16)
            key = _derive_key(self._passphrase, salt)
            f = Fernet(key)
            ciphertext = f.encrypt(plaintext.encode("utf-8"))
            salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
            ct_b64 = ciphertext.decode("ascii")
            return f"{salt_b64}${ct_b64}"
        except Exception as e:
            logger.error("encryption_failed", error=str(e))
            raise JarvisError(ErrorCode.ENCRYPTION_FAILED, detail=str(e)) from e

    def decrypt(self, encrypted: str) -> str:
        """Decrypt a salt$ciphertext string back to plaintext.

        Args:
            encrypted: String in format: base64(salt)$base64(ciphertext)

        Returns:
            Decrypted plaintext string.
        """
        try:
            parts = encrypted.split("$", 1)
            if len(parts) != 2:
                raise ValueError("Invalid encrypted format: expected salt$ciphertext")
            salt = base64.urlsafe_b64decode(parts[0])
            ciphertext = parts[1].encode("ascii")
            key = _derive_key(self._passphrase, salt)
            f = Fernet(key)
            return f.decrypt(ciphertext).decode("utf-8")
        except (InvalidToken, ValueError) as e:
            logger.error("decryption_failed", error=str(e))
            raise JarvisError(ErrorCode.DECRYPTION_FAILED, detail=str(e)) from e
        except Exception as e:
            logger.error("decryption_failed", error=str(e))
            raise JarvisError(ErrorCode.DECRYPTION_FAILED, detail=str(e)) from e
