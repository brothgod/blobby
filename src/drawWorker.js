let canvas = null;
let ctx = null;
let initialized = false;

self.onmessage = (event) => {
  console.log("Data sent to worker:", event.data);
  const { offscreenCanvas, points, color } = event.data;

  // Initialize canvas and context only once
  if (!initialized) {
    if (!offscreenCanvas) return;
    canvas = offscreenCanvas;
    ctx = offscreenCanvas.getContext("2d");
    initialized = true;
    console.log("initialized");
    return;
  }

  if (points.length < 2) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);

  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();

  const bitmap = canvas.transferToImageBitmap();
  self.postMessage(bitmap, [bitmap]); // Transfer the bitmap
};
