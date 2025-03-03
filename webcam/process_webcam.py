import cv2
import mediapipe as mp
import numpy as np
import threading
import time

# MediaPipe setup
#https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarker#detect_async
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Store latest result (thread-safe)
current_result = None
result_lock = threading.Lock()

def set_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    """Callback function to update segmentation mask result asynchronously."""
    global current_result
    with result_lock:
        current_result = result

def process_image(result):
    """Applies segmentation mask overlay."""
    if result is None or result.segmentation_masks is None:
        return None

    segmentation_mask = result.segmentation_masks[0].numpy_view()
    
    # Define colors
    MASK_COLOR = (0, 255, 0)  # Green
    BG_COLOR = (0, 0, 0)  # Black

    # Create color images (H, W, 3)
    fg_image = np.full((*segmentation_mask.shape, 3), MASK_COLOR, dtype=np.uint8)
    bg_image = np.full((*segmentation_mask.shape, 3), BG_COLOR, dtype=np.uint8)
    
    # Create condition mask (ensure it's properly thresholded)
    condition = np.stack((segmentation_mask,) * 3, axis=-1) > 0.2
    
    return np.where(condition, fg_image, bg_image)

# Load PoseLandmarker with async mode
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='webcam/pose_landmarker_full.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    output_segmentation_masks=True,
    result_callback=set_result
)

# Capture video from webcam or URL
stream_url = "http://localhost:5000/video_feed"
cap = cv2.VideoCapture(0)  # Use stream_url for remote feeds

frame_timestamp = 0

# Start a background thread to process frames
def frame_capture():
    global frame_timestamp
    with PoseLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_timestamp += 1
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            landmarker.detect_async(mp_image, frame_timestamp)

    cap.release()

# Start async frame capture thread
threading.Thread(target=frame_capture, daemon=True).start()

# Main display loop
while True:
    with result_lock:
        latest_result = current_result  # Copy latest result safely

    output_image = process_image(latest_result)
    
    if output_image is not None:
        cv2.imshow("Segmentation Mask", output_image)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
