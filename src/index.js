const socketOutput = document.getElementById("socketOutput");
const ws = new WebSocket("ws://localhost:3000", "master"); // Connect as master
const canvas = document.getElementById("myCanvas");
const ctx = canvas.getContext("2d");

ws.onopen = () => {
  socketOutput.textContent += "Connected as Master Client\n";
};

ws.onmessage = (event) => {
  // Print incoming messages from external clients
  // socketOutput.textContent += `Client: ${event.data}\n`;
  const points = JSON.parse(event.data);
  console.log(points);
  drawPolyline(points);
};

ws.onclose = () => {
  socketOutput.textContent += "Disconnected from server\n";
};

// Function to draw polyline on canvas
function drawPolyline(points) {
  if (points.length < 2) return; // Need at least two points to draw a line

  ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear previous drawings
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);

  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  ctx.strokeStyle = "#000000"; // Set line color
  ctx.lineWidth = 2; // Set line thickness
  ctx.stroke();
}
