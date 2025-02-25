import cv2
import mediapipe as mp
import math
import numpy as np

stream_url = "http://localhost:5000/video_feed"
cap = cv2.VideoCapture(0) #cv2.VideoCapture(stream_url)
mp_pose = mp.solutions.pose

BG_COLOR = (192, 192, 192) # gray
MASK_COLOR = (255, 255, 255) # white
with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2,
    enable_segmentation=True,
    min_detection_confidence=.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = pose.process(frame)

        if results.segmentation_mask is None:
            continue

        # Generate solid color images for showing the output selfie segmentation mask.
        fg_image = np.zeros(frame.shape, dtype=np.uint8)
        fg_image[:] = MASK_COLOR
        bg_image = np.zeros(frame.shape, dtype=np.uint8)
        bg_image[:] = BG_COLOR
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.2
        output_image = np.where(condition, fg_image, bg_image)

        cv2.imshow("Streamed Webcam", output_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
