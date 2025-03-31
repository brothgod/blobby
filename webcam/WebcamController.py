import mediapipe as mp
import threading
import websocket
import json
from Webcam import Webcam
import yaml

# MediaPipe setup
#https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarker#detect_async
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

class WebcamController:
    def __init__(self, webcam_list: list[str], use_websocket: bool, level: str = "full", canvas_side: int = 100):
        self.webcams = [Webcam(webcam_stream = stream, level=level, index=index, canvas_side = canvas_side) for index, stream in enumerate(webcam_list)]
        self.use_websocket = use_websocket
        
        if use_websocket:
            self.ws = websocket.WebSocket()
            self.ws.connect("ws://localhost:3000")

        for webcam in self.webcams:
            webcam.start_capture()
            threading.Thread(target=self._run_webcam, args=(webcam,), daemon=True).start()
            #TODO: change this to multiprocessing, and pass the websocket to the webcam so that it can do everything
    
    def _send_blob(self, points_list):
        self.ws.send(json.dumps(points_list))
    
    def _run_webcam(self, webcam: Webcam):
        while(True):
            try:
                index, output_image, blob = webcam.get_blob()
                if output_image is not None:
                    points_list = {f"blob":[{"x": int(x), "y": int(y)} for x, y in blob],  "index": index}
                    if(self.use_websocket):
                        self._send_blob(points_list)
                # cv2.imshow(f"blob_{index}", output_image)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            except:
                print("ERROR")


with open("constants.yaml", "r") as file:
    constants = yaml.safe_load(file)

webcam_list = [str(x) for x in range(constants["NUM_WEBCAMS"])]
use_websocket = constants["USE_WEBSOCKET"]
level = constants["POSE_LEVEL"]
canvas_side = constants["CANVAS_SIDE"]
webcam_controller = WebcamController(webcam_list=webcam_list, use_websocket=use_websocket, level=level, canvas_side = canvas_side)
while(True):
    do = "nothing"  