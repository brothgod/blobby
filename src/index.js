import constants from "../constants.json";

const numWebcams = constants["NUM_WEBCAMS"];
const numCanvases = constants["NUM_CANVASES"];
const canvasSide = constants["CANVAS_SIDE"];
const socketOutput = document.getElementById("socket-output");
const ws = new WebSocket("ws://localhost:3000", "master"); // Connect as master

const canvasContainer = document.getElementById("canvas-container");
//The master canvases, which the rendering is done on
const offscreenCanvases = [];
for (let i = 0; i < numWebcams; i++) {
  let masterCanvas = document.createElement("canvas");
  masterCanvas.width = canvasSide;
  masterCanvas.height = canvasSide;
  masterCanvas.classList.add("masterCanvas");
  masterCanvas.id = `master-canvas-${i}`;
  let offscreenCanvas = masterCanvas.transferControlToOffscreen();
  let ctxList = [];
  for (let j = 0; j < numCanvases; j++) {
    let canvas = document.createElement("canvas");
    canvas.width = canvasSide;
    canvas.height = canvasSide;
    canvas.classList.add(`canvas-${i}`);
    let ctx = canvas.getContext("2d");
    ctxList.push(ctx);
    canvasContainer.appendChild(canvas);
  }

  offscreenCanvases.push({ offscreenCanvas, ctxList });
}

const workers = offscreenCanvases.map(({ offscreenCanvas, ctxList }, index) => {
  const worker = new Worker(new URL("drawWorker.js", import.meta.url));
  worker.postMessage({ offscreenCanvas }, [offscreenCanvas]);
  worker.onmessage = (event) => {
    console.log("Got data back from worker", event.data);
    const bitmap = event.data;
    ctxList.forEach((ctx, i) => {
      // Draw the bitmap onto the main thread canvas
      ctx.clearRect(0, 0, canvasSide, canvasSide);
      ctx.drawImage(bitmap, 0, 0);
    });
  };
  return worker;
});
const colors = ["#ff005a", "#ff8818", "#6cbb00"];

ws.onopen = () => {
  socketOutput.textContent += "Connected as Master Client\n";
};

ws.onmessage = (event) => {
  const data_json = JSON.parse(event.data);
  console.log("Got message from WebSocket:", data_json);
  const points = data_json.blob;
  const index = parseInt(data_json.index);

  if (points.length < 2) return;

  const worker = workers[index];
  worker.postMessage({
    points,
    color: colors[index],
  });
};

ws.onclose = () => {
  socketOutput.textContent += "Disconnected from server\n";
};
