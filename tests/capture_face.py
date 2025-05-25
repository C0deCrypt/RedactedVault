import cv2
import os


def capture_fixture(output_path='fixtures/face2.jpg'):
    """
    Capture a single face image from the default webcam and save it
    for use as a test fixture (e.g., face authentication tests).

    Usage:
        1. Run this script: python capture_fixture.py
        2. A window will open showing the webcam feed.
        3. Press 's' to capture and save the current frame.
        4. The fixture will be saved at tests/fixtures/face.jpg
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam. Check your camera device.")

    print("=== Fixture Capture ===")
    print("Press 's' in the window to capture your face and save as fixture.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Capture Fixture", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            # Save the frame
            cv2.imwrite(output_path, frame)
            print(f"Fixture saved to {output_path}")
            break
        elif key == ord('q'):
            print("Capture aborted by user.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    capture_fixture()
