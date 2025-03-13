const socketOutput = document.getElementById("socketOutput");
const ws = new WebSocket("ws://localhost:3000", "master"); // Connect as master
const canvases = [
  document.getElementById("canvas-0"),
  document.getElementById("canvas-1"),
  document.getElementById("canvas-2"),
  document.getElementById("canvas-3"),
];
const colors = ["#ff005a", "#ff8818", "#6cbb00"];

const ctxs = canvases.map((canvas) => canvas.getContext("2d"));

ws.onopen = () => {
  socketOutput.textContent += "Connected as Master Client\n";
};

ws.onmessage = (event) => {
  // Print incoming messages from external clients
  // socketOutput.textContent += `Client: ${event.data}\n`;
  const data_json = JSON.parse(event.data);
  const points = data_json.blob;
  // console.log(data_json);
  const index = parseInt(data_json.index);
  drawPolyline(index, points);
};

ws.onclose = () => {
  socketOutput.textContent += "Disconnected from server\n";
};

// Function to draw polyline on canvas
function drawPolyline(index, points) {
  const ctx = ctxs[index];
  if (points.length < 2) return; // Need at least two points to draw a line

  ctx.clearRect(0, 0, canvases[index].width, canvases[index].height); // Clear previous drawings
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);

  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  ctx.closePath();
  ctx.fillStyle = colors[index];
  ctx.fill();
}
