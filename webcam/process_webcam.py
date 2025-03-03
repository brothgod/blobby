import cv2
import mediapipe as mp
import numpy as np
import mediapipe as mp
import time

#https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarker#detect_async

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

current_result = None
# Create a pose landmarker instance with the live stream mode:
def set_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global current_result
    current_result = result

BG_COLOR = (192, 192, 192) # gray
MASK_COLOR = (255, 255, 255) # white
# def process_image(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
def process_image(result):
    if result is not None and result.segmentation_masks is not None:
        # Convert segmentation mask to a NumPy array
        segmentation_mask = result.segmentation_masks[0].numpy_view()
        
        # Define colors
        MASK_COLOR = (0, 255, 0)  # Green
        BG_COLOR = (0, 0, 0)  # Black

        # Create color images (H, W, 3)
        fg_image = np.full((*segmentation_mask.shape, 3), MASK_COLOR, dtype=np.uint8)
        bg_image = np.full((*segmentation_mask.shape, 3), BG_COLOR, dtype=np.uint8)
        
        # Create condition mask (ensure it's properly thresholded)
        condition = np.stack((segmentation_mask,) * 3, axis=-1) > 0.2
        # Apply mask using np.where()
        
        output_image = np.where(condition, fg_image, bg_image)
        return output_image
        

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='C:/Users/menon/OneDrive/Documents/NYC/blobby/webcam/pose_landmarker_heavy.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    output_segmentation_masks=True,
    result_callback=set_result)

stream_url = "http://localhost:5000/video_feed"
# cap = cv2.VideoCapture(stream_url)
cap = cv2.VideoCapture(0) 
mp_pose = mp.solutions.pose
frame_timestamp = 0

with PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        timestamp = int(round(time.time() * 1000))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        landmarker.detect_async(mp_image, timestamp)
        output_image = process_image(current_result)
        if output_image is not None:
            cv2.imshow("Segmentation Mask", output_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        frame_timestamp+=1

    cap.release()
    cv2.destroyAllWindows()
