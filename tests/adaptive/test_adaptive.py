import os
import numpy as np
import pytest

from fingerprint.match_utils import preprocess_fingerprint, extract_minutiae, compare_minutiae

# Image dimensions from your match_template
IMG_WIDTH, IMG_HEIGHT = 260, 300
# Adjust path if needed (fixtures folder two levels up)
FIXTURE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'fixtures')
)

# Matching thresholds
MATCH_THRESHOLD = 0.70    # expected match threshold
TOLERANCE = 0.05         # allowable tolerance around threshold


def load_dat(filename):
    """
    Load raw fingerprint data from .dat file and reshape into image array.
    """
    path = os.path.join(FIXTURE_DIR, filename)
    with open(path, 'rb') as f:
        raw = f.read()
    assert len(raw) == IMG_WIDTH * IMG_HEIGHT, \
        f"Unexpected size for {filename}: {len(raw)} bytes"
    return np.frombuffer(raw, dtype=np.uint8).reshape((IMG_HEIGHT, IMG_WIDTH))


@pytest.mark.parametrize(
    "file1,file2,expected_match",
    [
        ("fingerprint.dat", "fingerprint.dat", True),    # identical prints
        ("fingerprint.dat", "fingerprint2.dat", False),  # different prints
    ]
)
def test_adaptive_random_fingerprint(file1, file2, expected_match):
    """
    Adaptive-style test that checks if two fingerprint images match above or below thresholds.
    """
    # Load raw images
    img1 = load_dat(file1)
    img2 = load_dat(file2)

    # Preprocess to skeletons
    skel1 = preprocess_fingerprint(img1)
    skel2 = preprocess_fingerprint(img2)

    # Extract minutiae
    min1 = extract_minutiae(skel1)
    min2 = extract_minutiae(skel2)

    # Compare and compute match ratio
    matches, total1, total2 = compare_minutiae(min1, min2, dist_thresh=10)
    ratio = matches / max(len(min2), 1)

    # Determine acceptable bounds
    lower_bound = MATCH_THRESHOLD - TOLERANCE
    upper_bound = MATCH_THRESHOLD + TOLERANCE

    if expected_match:
        assert ratio >= lower_bound, \
            f"Expected match ratio >= {lower_bound:.2f}, but got {ratio:.3f}"
    else:
        assert ratio <= upper_bound, \
            f"Expected mismatch ratio <= {upper_bound:.2f}, but got {ratio:.3f}"
