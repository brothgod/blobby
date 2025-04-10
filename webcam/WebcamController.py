import mediapipe as mp
import json
from Webcam import Webcam
from multiprocessing import Process

# MediaPipe setup
#https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarker#detect_async
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

class WebcamController:
    def __init__(self, webcam_list: list[str], use_websocket: bool, websocket_port: int, level: str = "full"):
        ws_address = f"ws://localhost:{websocket_port}" if use_websocket else None
        self.webcams = [Webcam(webcam_stream = stream, level=level, index=index, ws_address=ws_address) for index, stream in enumerate(webcam_list)]

        for webcam in self.webcams:
            if use_websocket:
                Process(target=webcam.generate_blobs, daemon=True).start()
            else:
                webcam.generate_blobs()

if __name__ == '__main__':
    with open("constants.json", "r") as file:
        constants = json.load(file)

    webcam_list = [str(x) for x in range(constants["NUM_WEBCAMS"])]
    use_websocket = constants["USE_WEBSOCKET"]
    level = constants["POSE_LEVEL"]
    websocket_port = constants["WEBSOCKET_PORT"]
    webcam_controller = WebcamController(webcam_list=webcam_list, use_websocket=use_websocket, websocket_port =  websocket_port, level=level)
    while(True):
        pass