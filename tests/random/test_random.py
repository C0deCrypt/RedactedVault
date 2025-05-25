
import os
import secrets
from pathlib import Path

from cryptography.fernet import Fernet


SECRET_KEY_FILE = Path("secret.key")


def _get_or_make_key():
    if SECRET_KEY_FILE.exists():
        return SECRET_KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    SECRET_KEY_FILE.write_bytes(key)
    return key


def test_fernet_round_trip(tmp_path):
    """Vault encryption key must correctly decrypt encrypted payloads."""
    key = _get_or_make_key()
    f = Fernet(key)

    original = secrets.token_bytes(1024)  # 1 KiB random data
    token = f.encrypt(original)
    recovered = f.decrypt(token)

    assert original == recovered, "Decrypted bytes do not match original."


def test_multiple_round_trips(tmp_path):
    """Multiple encryptions with the same key should all decrypt successfully."""
    key = _get_or_make_key()
    f = Fernet(key)

    for _ in range(10):
        data = secrets.token_bytes(256)
        token = f.encrypt(data)
        assert f.decrypt(token) == data
