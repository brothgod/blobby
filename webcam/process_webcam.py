import cv2
import mediapipe as mp
import math
import numpy as np
import mediapipe as mp
import time

#https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarker#detect_async

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a pose landmarker instance with the live stream mode:
def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    print('pose landmarker result: {}'.format(result))

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='/Users/aditigupta/Documents/nyu/classes/thesis/blobby/webcam/pose_landmarker_heavy.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

stream_url = "http://localhost:5000/video_feed"
# cap = cv2.VideoCapture(stream_url)
cap = cv2.VideoCapture(0) 
mp_pose = mp.solutions.pose

BG_COLOR = (192, 192, 192) # gray
MASK_COLOR = (255, 255, 255) # white
frame = 0
with PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        landmarker.detect_async(mp_image, frame)

        # if results.segmentation_mask is None:
        #     continue

        # # Generate solid color images for showing the output selfie segmentation mask.
        # fg_image = np.zeros(frame.shape, dtype=np.uint8)
        # fg_image[:] = MASK_COLOR
        # bg_image = np.zeros(frame.shape, dtype=np.uint8)
        # bg_image[:] = BG_COLOR
        # condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.2
        # output_image = np.where(condition, fg_image, bg_image)

        # cv2.imshow("Streamed Webcam", output_image)

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        frame+=1

    cap.release()
    cv2.destroyAllWindows()
