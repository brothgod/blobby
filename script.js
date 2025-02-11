import * as poseDetection from "@tensorflow-models/pose-detection";
import "@tensorflow/tfjs-core";
// Register WebGL backend.
import "@tensorflow/tfjs-backend-webgl";
import "@mediapipe/pose";

const model = poseDetection.SupportedModels.BlazePose;
const detectorConfig = {
  runtime: "mediapipe",
  solutionPath: "base/node_modules/@mediapipe/pose",
  // https://cdn.jsdelivr.net/npm/@mediapipe/pose
  // or 'base/node_modules/@mediapipe/pose' in npm.
};
detector = await poseDetection.createDetector(model, detectorConfig);

const estimationConfig = { enableSmoothing: true };
const poses = await detector.estimatePoses(image, estimationConfig);
