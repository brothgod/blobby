import constants from "../constants.json";
import { generateTilePattern, buildCanvasGrid } from "./canvasPattern.ts";

const numWebcams = constants["NUM_WEBCAMS"];
const socketOutput = document.getElementById("socket-output");
const ws = new WebSocket("ws://localhost:3000", "master"); // Connect as master
let rows = 3;
let cols = 5;

const canvasContainer = document.getElementById("canvas-container");
let tilePattern = generateTilePattern(numWebcams, rows, cols, 0);
let ctxLists = buildCanvasGrid(tilePattern, numWebcams, canvasContainer);

canvasContainer.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
canvasContainer.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

const updateRowCols = (newRows, newCols) => {
  rows = newRows;
  cols = newCols;
  canvasContainer.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
  canvasContainer.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  tilePattern = generateTilePattern(numWebcams, rows, cols, 0);
  ctxLists = buildCanvasGrid(tilePattern, numWebcams, canvasContainer);
};

//The master canvases, which the rendering is done on
const offscreenCanvases = [];
for (let i = 0; i < numWebcams; i++) {
  let masterCanvas = document.createElement("canvas");
  masterCanvas.classList.add("masterCanvas");
  masterCanvas.id = `master-canvas-${i}`;
  let offscreenCanvas = masterCanvas.transferControlToOffscreen();
  offscreenCanvases.push(offscreenCanvas);
}

const workerStatuses = offscreenCanvases.map(() => {
  return { busy: false, latestData: null };
});
const workers = offscreenCanvases.map((offscreenCanvas, index) => {
  const worker = new Worker(new URL("drawWorker.js", import.meta.url));
  worker.postMessage({ offscreenCanvas }, [offscreenCanvas]);
  worker.onmessage = (event) => {
    console.log("Got data back from worker", event.data);
    const bitmap = event.data;
    ctxLists[index].forEach((ctx, i) => {
      // Draw the bitmap onto the main thread canvas
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
      ctx.drawImage(bitmap, 0, 0, ctx.canvas.width, ctx.canvas.height);
    });
    workerStatuses[index].busy = false;
    if (workerStatuses[index].latestData) {
      const data = workerStatuses[index].latestData;
      workerStatuses[index].latestData = null;
      sendToWorker(data, index);
    }
  };
  return worker;
});

const colors = ["#ff005a", "#ff8818", "#6cbb00"];
function sendToWorker(data, index) {
  const worker = workers[index];
  const workerStatus = workerStatuses[index];
  if (workerStatus.busy) {
    // Save latest frame only
    workerStatus.latestData = data;
    return;
  }

  const points = data.blob;

  if (points.length < 2) return;

  worker.postMessage({
    points,
    color: colors[index],
    height: data.height,
    width: data.width,
  });
  workerStatus.busy = true;
}

ws.onopen = () => {
  socketOutput.textContent += "Connected as Master Client\n";
};

ws.onmessage = (event) => {
  const data_json = JSON.parse(event.data);
  console.log("Got message from WebSocket:", data_json);
  sendToWorker(data_json, parseInt(data_json.index));
};

ws.onclose = () => {
  socketOutput.textContent += "Disconnected from server\n";
};

document.addEventListener("keydown", (event) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
    event.preventDefault(); // Stops scrolling
    console.log(`${event.key} pressed, but scroll prevented`);
  }
});

// Listen for keyup event on the entire document
document.addEventListener("keyup", (event) => {
  let newRows = rows;
  let newCols = cols;
  switch (event.key) {
    case "ArrowUp":
      newRows--;
      break;
    case "ArrowDown":
      newRows++;
      break;
    case "ArrowLeft":
      newCols--;
      break;
    case "ArrowRight":
      newCols++;
      break;
    default:
      break;
  }

  updateRowCols(Math.max(newRows, 1), Math.max(newCols, 1));
});
