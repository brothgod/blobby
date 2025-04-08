import json
import traceback
import cv2
import mediapipe as mp
import numpy as np
from scipy.interpolate import CubicSpline
import asyncio

import websocket

# MediaPipe setup
#https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarker#detect_async
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

class Webcam:
    def __init__(self, webcam_stream: str, index: str, level:str = "full", ws_address:str =None ):
        self.webcam_stream = webcam_stream
        self.current_mask = None
        self.ws_address = ws_address
        self.options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=f'webcam/pose_landmarker_{level}.task'),
            running_mode=VisionRunningMode.LIVE_STREAM,
            output_segmentation_masks=True,
            result_callback=self._process_image
        )
        self.frame_timestamp = 0
        self.index = index

    def _connect_to_websocket(self):
        self.ws = websocket.WebSocket()
        self.ws.connect(self.ws_address)
    
    def _send_blob(self, index, output_image, blob, width, height):
        if output_image is not None:
            points_list = {f"blob":[{"x": int(x), "y": int(y)} for x, y in blob],  "index": index, "height": height, "width": width}
            if(self.ws):
                self.ws.send(json.dumps(points_list))
        # print("Sent blob")

    def generate_blobs(self):
        if self.webcam_stream.isdigit():
            self.cap = cv2.VideoCapture(int(self.webcam_stream))
        else:
            self.cap = cv2.VideoCapture(self.webcam_stream)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if self.ws_address:
            self._connect_to_websocket()

        try:
            with PoseLandmarker.create_from_options(self.options) as landmarker:
                while self.cap.isOpened():
                    # print(f"Loop started: {self.frame_timestamp}")
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        break

                    # Step 1: Make the frame square
                    height, width, _ = frame.shape
                    min_dim = min(height, width)  # Choose the smaller dimension

                    # Crop the frame to be square (centered crop)
                    center_x, center_y = width // 2, height // 2
                    cropped_frame = frame[center_y - min_dim // 2:center_y + min_dim // 2, 
                                        center_x - min_dim // 2:center_x + min_dim // 2]

                    # Step 2: Convert BGR (OpenCV) to RGB
                    cropped_frame_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)

                    # Optional: Ensure data is contiguous (can help in some mediapipe backends)
                    cropped_frame_rgb = np.ascontiguousarray(cropped_frame_rgb)

                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cropped_frame_rgb)
                    # threading.Event()
                    # asyncio.run(landmarker.detect_async(mp_image, self.frame_timestamp))
                    landmarker.detect_async(mp_image, self.frame_timestamp)
                    # print(f"Loop over: {self.frame_timestamp}")
                    self.frame_timestamp += 1

        except Exception as e:
            print(f"ERROR: {e}")
            stack_trace = traceback.format_exc()
            print("Stack trace:\n" + stack_trace)
        self.cap.release()
        
    def _process_image(self, result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        """Applies segmentation mask overlay."""
        # print(f"Started image processing: {self.frame_timestamp}")
        if result is None or result.segmentation_masks is None:
            return None, None, None

        segmentation_mask = result.segmentation_masks[0].numpy_view()
        width = output_image.width
        height = output_image.height
        
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

        # return self.index, bg_image, curve_points  # Return image with contours drawn
        self._send_blob(self.index, bg_image, curve_points, width, height)  # Return image with contours drawn)