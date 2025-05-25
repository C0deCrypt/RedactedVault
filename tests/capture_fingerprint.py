import os
import sys
import subprocess
import json
import pickle
import numpy as np
from cryptography.fernet import Fernet
from fingerprint.match_utils import preprocess_fingerprint, extract_minutiae
from fingerprint.store_template import generate_key_if_missing, load_key

# Compute project root (one level up from tests directory)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def capture_fingerprint_fixture(
        exe_path=None,
        username='fixture_fp',
        dat_dir=None,
        fixture_path=None
):
    """
    Capture a real fingerprint via the SecuGen sensor executable,
    process it into a minutiae template, encrypt it, and save to a fixture file.

    - exe_path: path to CaptureFingerprint.exe
    - username: the identifier passed to the exe, and name of the .dat
    - dat_dir: directory where <username>.dat is written by the exe
    - fixture_path: output encrypted template fixture
    """

    # Set defaults relative to project root
    if exe_path is None:
        exe_path = os.path.join(
            PROJECT_ROOT,
            'fingerprint', 'capture', 'CaptureFingerprint', 'x64', 'Debug', 'CaptureFingerprint.exe'
        )
    if dat_dir is None:
        dat_dir = os.path.join(PROJECT_ROOT, 'fingerprint', 'fingerprints')
    if fixture_path is None:
        fixture_path = os.path.join(PROJECT_ROOT, 'tests', 'fixtures', 'fingerprint2.bin')

    # Ensure fixtures directory exists
    os.makedirs(os.path.dirname(fixture_path), exist_ok=True)

    print("=== Fingerprint Fixture Capture ===")
    print(f"Running capture executable: {exe_path}")

    # Step 1: call the sensor executable
    if not os.path.isfile(exe_path):
        print(f"[ERROR] Capture executable not found at {exe_path}")
        sys.exit(1)
    try:
        subprocess.run([exe_path, username], check=True)
        print(f"[OK] SecuGen capture for '{username}' completed.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] SecuGen capture failed: {e}")
        sys.exit(1)

    # Step 2: read raw .dat
    dat_file = os.path.join(dat_dir, f"{username}.dat")
    if not os.path.exists(dat_file):
        print(f"[ERROR] .dat file not found: {dat_file}")
        sys.exit(1)

    raw = open(dat_file, 'rb').read()
    IMG_WIDTH, IMG_HEIGHT = 260, 300
    img = np.frombuffer(raw, dtype=np.uint8).reshape((IMG_HEIGHT, IMG_WIDTH))
    print(f"[OK] Raw fingerprint data loaded ({len(raw)} bytes).")

    # Step 3: preprocess & extract
    skeleton = preprocess_fingerprint(img)
    minutiae = extract_minutiae(skeleton)
    print(f"[OK] Preprocessed and extracted {len(minutiae)} minutiae points.")

    # Step 4: encrypt
    generate_key_if_missing()
    master_key = load_key()
    fernet = Fernet(master_key)
    data_json = json.dumps(minutiae)
    encrypted = fernet.encrypt(data_json.encode())
    print(f"[OK] Encrypted template length: {len(encrypted)} bytes.")

    # Step 5: save fixture
    with open(fixture_path, 'wb') as f:
        f.write(encrypted)
    print(f"[SUCCESS] Fingerprint fixture saved to {fixture_path}.")


if __name__ == '__main__':
    capture_fingerprint_fixture()
