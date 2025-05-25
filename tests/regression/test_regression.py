import os
import sys
import json
import numpy as np
import pytest
from cryptography.fernet import Fernet

# Ensure project root (two levels up) is on PYTHONPATH
test_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(test_dir, '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

# Read master key directly from project root
KEY_PATH = os.path.join(PROJECT_ROOT,'tests','secret.key')
# Path to fingerprint fixture
FIXTURE = os.path.join(PROJECT_ROOT, 'tests', 'fixtures', 'fingerprint.bin')

# Import necessary comparison function
from fingerprint.match_utils import compare_minutiae


def test_fingerprint_self_match():
    """
    Regression test: A captured fingerprint template should match itself with maximal matches.
    """
    print("\n[TEST START] Fingerprint regression: self-match")

    # Check fixture and key exist
    print(f"[CHECK] Does fixture exist? {FIXTURE}: {os.path.exists(FIXTURE)}")
    print(f"[CHECK] Does master key exist? {KEY_PATH}: {os.path.exists(KEY_PATH)}")
    assert os.path.exists(FIXTURE), f"Fingerprint fixture not found at {FIXTURE}"
    assert os.path.exists(KEY_PATH), f"Master key not found at {KEY_PATH}"

    # Load encrypted fixture
    print(f"[INFO] Loading fixture from {FIXTURE}")
    cipher = open(FIXTURE, 'rb').read()

    # Load master key
    print(f"[INFO] Loading master key from {KEY_PATH}")
    master_key = open(KEY_PATH, 'rb').read()
    fernet = Fernet(master_key)

    # Decrypt
    raw_json = fernet.decrypt(cipher).decode()
    minutiae = json.loads(raw_json)
    print(f"[INFO] Loaded {len(minutiae)} minutiae points")

    # Self-match
    print("[INFO] Matching minutiae list against itself")
    matches, count1, count2 = compare_minutiae(minutiae, minutiae)
    print(f"[RESULT] {matches}/{count1} matched")

    # Assertions: all points should match
    assert matches == count1 == count2, (
        f"Expected all minutiae to match, got {matches}/{count1}")
    print("[PASS] Fingerprint self-match regression test passed")
