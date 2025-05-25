import os
import sys
import cv2
import numpy as np
import pytest
import face_recognition

# Make sure our project modules are importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# Path to the captured fixture
ORIG_IMG_PATH = os.path.join(PROJECT_ROOT,  'fixtures', 'face.jpg')

# Threshold from face_auth.py
DIST_THRESHOLD = 0.6

def transform_image(image, kind):
    h, w = image.shape[:2]
    if kind == 'rotate':
        M = cv2.getRotationMatrix2D((w/2, h/2), 10, 1.0)
        return cv2.warpAffine(image, M, (w, h))
    if kind == 'scale':
        return cv2.resize(image, None, fx=1.1, fy=1.1)
    if kind == 'bright':
        return cv2.convertScaleAbs(image, alpha=1.2, beta=10)
    raise ValueError(f"Unknown transform {kind}")

@pytest.mark.parametrize("transform", ['rotate', 'scale', 'bright'])
def test_face_metamorphic(transform):
    print(f"\n[TEST START] Metamorphic face test: {transform}")

    # Load and encode original
    if not os.path.exists(ORIG_IMG_PATH):
        pytest.skip(f"No fixture at {ORIG_IMG_PATH}")
    orig_img = face_recognition.load_image_file(ORIG_IMG_PATH)
    orig_encs = face_recognition.face_encodings(orig_img)
    assert orig_encs, f"No face found in fixture for {transform}"
    orig_enc = orig_encs[0]

    # Use the same encoding as 'stored'
    stored_enc = orig_enc

    # Apply transform and re-encode
    bgr    = cv2.cvtColor(orig_img, cv2.COLOR_RGB2BGR)
    img_t  = transform_image(bgr, transform)
    rgb_t  = cv2.cvtColor(img_t, cv2.COLOR_BGR2RGB)
    encs_t = face_recognition.face_encodings(rgb_t)
    assert encs_t, f"Face missing after {transform}"
    enc_t = encs_t[0]

    # Compute distance
    dist = np.linalg.norm(stored_enc - enc_t)
    print(f"[MR={transform}] distance = {dist:.3f} (threshold = {DIST_THRESHOLD})")

    # Assert invariance
    assert dist <= DIST_THRESHOLD, f"Distance too large after {transform}: {dist}"

    print(f"[PASS] Metamorphic face test: {transform}")
