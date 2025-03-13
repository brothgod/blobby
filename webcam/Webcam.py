import cv2
import mediapipe as mp
import numpy as np
import threading
import websocket
import json
from scipy.interpolate import CubicSpline

# MediaPipe setup
#https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarker#detect_async
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

class Webcam:
    def __init__(self, webcam_stream: str, index: str, level:str = "full" ):
        if webcam_stream.isdigit():
            self.cap = cv2.VideoCapture(int(webcam_stream))
        else:
            self.cap = cv2.VideoCapture(webcam_stream)
        self.current_mask = None
        self.frame_lock = threading.Lock()
        self.options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=f'webcam/pose_landmarker_{level}.task'),
            running_mode=VisionRunningMode.LIVE_STREAM,
            output_segmentation_masks=True,
            result_callback=self._set_current_mask
        )
        self.frame_timestamp = 0
        self.index = index

    def start_capture(self):
        threading.Thread(target=self._frame_capture, daemon=True).start()

    def _frame_capture(self):
        with PoseLandmarker.create_from_options(self.options) as landmarker:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                self.frame_timestamp += 1
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                landmarker.detect_async(mp_image, self.frame_timestamp)
        self.cap.release()
    
    def _set_current_mask(self, result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        with self.frame_lock:
            self.current_mask = result
    
    def get_blob(self):
        with self.frame_lock:
            latest_result = self.current_mask  # Copy latest result safely
        return self._process_image(latest_result)
        
    def _process_image(self, result):
        """Applies segmentation mask overlay."""
        if result is None or result.segmentation_masks is None:
            return None, None, None

        segmentation_mask = result.segmentation_masks[0].numpy_view()
        
        # Define colors
        MASK_COLOR = (255, 255, 255)  # White
        BG_COLOR = (0, 0, 0)  # Black

        # Create color images (H, W, 3)
        fg_image = np.full((*segmentation_mask.shape, 3), MASK_COLOR, dtype=np.uint8)
        bg_image = np.full((*segmentation_mask.shape, 3), BG_COLOR, dtype=np.uint8)
        
        # Create condition mask (ensure it's properly thresholded)
        condition = np.stack((segmentation_mask,) * 3, axis=-1) > 0.2
        mask_image = np.where(condition, fg_image, bg_image)

        # Convert to grayscale for contour detection
        gray_mask = cv2.cvtColor(mask_image, cv2.COLOR_BGR2GRAY)

        # Find contours
        contours, hierarchy = cv2.findContours(gray_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # If there are no contours, return None
        if not contours:
            return None, None, None

        # Find the largest contour based on area
        contour = max(contours, key=cv2.contourArea)
        convexity_factor = .01
        # Approximate the convex hull polygon (smooths edges)
        epsilon = convexity_factor * cv2.arcLength(contour, True)
        approx_hull = cv2.approxPolyDP(contour, epsilon, True)
        curve_points = None

        if len(approx_hull) > 2:  # At least 3 points for a curve
            points = approx_hull.reshape(-1, 2)
            x = points[:, 0]
            y = points[:, 1]
            
            # Fit cubic spline to the points
            spline_x = CubicSpline(np.arange(len(x)), x, bc_type='natural')
            spline_y = CubicSpline(np.arange(len(y)), y, bc_type='natural')
            
            # Generate smoothed points along the spline
            smooth_points = np.linspace(0, len(x)-1, num=100)
            smooth_x = spline_x(smooth_points).astype(np.int32)
            smooth_y = spline_y(smooth_points).astype(np.int32)
            
            # Draw the smooth curve
            curve_points = np.vstack((smooth_x, smooth_y)).T
            cv2.polylines(bg_image, [curve_points], isClosed=True, color=(255, 255, 255), thickness=2)

        return self.index, bg_image, curve_points  # Return image with contours drawn