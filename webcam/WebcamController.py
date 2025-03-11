import cv2
import mediapipe as mp
import numpy as np
import threading
import websocket
import json
from scipy.interpolate import CubicSpline
from Webcam import Webcam

# MediaPipe setup
#https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarker#detect_async
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

class WebcamController:
    def __init__(self, rtsp_list: list[str], local_webcam: bool, level: str):
        if local_webcam:
            self.webcams = [Webcam(level=level)]
        else:
            self.webcams = [Webcam(webcam_rtsp = rtsp, level=level) for rtsp in rtsp_list]
        
        self.ws = websocket.WebSocket()
        self.ws.connect("ws://localhost:3000")

        self.blob_locks = []
        for webcam in self.webcams:
            webcam.start_capture()
            self.blob_locks.push(threading.Lock())
        
    def _get_blob(webcam: Webcam):
        return
    
    def _set_blob(webcam: Webcam):
        return
    
    def _send_blob(self, index):
        points_list = {f"blob_{index}":[{"x": int(x), "y": int(y)} for x, y in blob]}
        print(json.dumps(points_list))
        self.ws.send(json.dumps(points_list))
    
    def _run_webcam(self,webcam: Webcam):
        while(True):
            output_image, blob = webcam.get_blob()
            points_list = {"blob":[{"x": int(x), "y": int(y)} for x, y in blob]}
            if output_image is not None:
                self._send_blob(blob)
                cv2.imshow("blobby", output_image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    