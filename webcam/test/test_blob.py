import sys
import os
import mediapipe as mp

# Add the parent directory to the sys.path so you can import Webcam
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Webcam import Webcam
folder_path = "webcam/test/input_images"  # change this to your folder path

a = Webcam()
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult

for filename in os.listdir(folder_path):
    if filename.endswith(".png"):
        print(f"Processing {filename}...")
        file_path = os.path.join(folder_path, filename)
        # Do something with the image
        img = mp.Image.create_from_file(file_path)
        result = PoseLandmarkerResult(segmentation_masks=[img], pose_landmarks=[], pose_world_landmarks=[])
        a._process_image(result, img, -1)
