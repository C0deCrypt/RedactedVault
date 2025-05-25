# tests/test_oracle/test_oracle.py
import os
import builtins
import pytest
from cryptography.fernet import Fernet
import fingerprint.match_template as match_mod

# Paths to your fixtures
FIX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fixtures"))
SECRET_KEY_PATH = os.path.join(FIX_DIR, "secret.key")
ALICE_BIN       = os.path.join(FIX_DIR, "fingerprint.bin")
BOB_BIN         = os.path.join(FIX_DIR, "fingerprint2.bin")
ALIVE_DAT       = os.path.join(FIX_DIR, "fingerprint.dat")
BLIVE_DAT       = os.path.join(FIX_DIR, "fingerprint2.dat")

# Preload all fixture data once
with open(SECRET_KEY_PATH, "rb") as f:
    MASTER_KEY = f.read()
with open(ALICE_BIN, "rb") as f:
    ALICE_ENC = f.read()
with open(BOB_BIN, "rb") as f:
    BOB_ENC = f.read()
with open(ALIVE_DAT, "rb") as f:
    ALIVE_RAW = f.read()
with open(BLIVE_DAT, "rb") as f:
    BLIVE_RAW = f.read()

@pytest.fixture(autouse=True)
def stub_everything(monkeypatch):
    # 1) Stub out fetch_user_biometric(username, "finger")
    def fake_fetch(username, kind):
        if username == "alice":
            return username, ALICE_ENC
        if username == "bob":
            return username, BOB_ENC
        return username, None
    monkeypatch.setattr(match_mod, "fetch_user_biometric", fake_fetch)

    # 2) Stub out get_user_unlock_code(username)
    monkeypatch.setattr(match_mod, "get_user_unlock_code", lambda u: "dummy")

    # 3) Stub out load_key() to return our secret.key
    monkeypatch.setattr(match_mod, "load_key", lambda: MASTER_KEY)

    # 4) Make sure authenticate_fingerprint sees a “live.dat” file & can open it
    #    We intercept os.path.exists and builtins.open for just those two paths.
    monkeypatch.setattr(os.path, "exists", lambda p: True)

    real_open = builtins.open
    def fake_open(path, mode="rb", *args, **kwargs):
        # live scan for alice
        if path.endswith("alice_live.dat"):
            return real_open(ALIVE_DAT, mode)
        # live scan for bob
        if path.endswith("bob_live.dat"):
            return real_open(BLIVE_DAT, mode)
        # everything else (including the Fernet fixtures) goes through
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)

@pytest.mark.parametrize("username, expected", [
    ("alice", True),   # genuine pair → should succeed
    ("bob",   False),  # mismatch    → should fail
])
def test_oracle_matches(username, expected):
    """
    Oracle:
      - A genuine template/live pair should authenticate (alice → True)
      - A mismatched pair should fail       (bob   → False)
    """
    result = match_mod.authenticate_fingerprint(username)
    assert result is expected
