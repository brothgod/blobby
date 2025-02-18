import simplify from "simplify-js";
import convexHull from "convex-hull";

interface Point {
  x: number;
  y: number;
}

export function blobifyMask(imageData: ImageData): ImageData {
  const binaryMask: number[][] = imageDataToBinary(imageData);
  const contour: Point[] = findCoutour(binaryMask);
  // const simplifiedContour = simplifyContour(contour);
  const hull = contourToHull(contour);
  const contourImage: ImageData = contourToImageData(
    hull,
    imageData.width,
    imageData.height
  );

  return contourImage;
}

function imageDataToBinary(imageData: ImageData): number[][] {
  const { data, width, height } = imageData;
  const binaryMask = new Array(width)
    .fill(0)
    .map(() => new Array(height).fill(0));

  var ones = 0;
  var zeros = 0;

  for (let x = 0; x < width; x++) {
    for (let y = 0; y < height; y++) {
      const index = (y * width + x) * 4; // RGBA format
      const r = data[index];
      const g = data[index + 1];
      const b = data[index + 2];

      // If the pixel is isn't [0,0,0,0]
      if (r === 0 && b === 0 && g === 0) {
        zeros += 1;
      } else {
        binaryMask[x][y] = 1; // Mark as contour
        ones += 1;
      }
    }
  }
  return binaryMask;
}

function findCoutour(binaryMask: number[][]): Point[] {
  const rows = binaryMask.length;
  const cols = binaryMask[0].length;

  // Define 8-connected neighbor directions (clockwise order)
  const directions = [
    [-1, 0],
    [-1, 1],
    [0, 1],
    [1, 1],
    [1, 0],
    [1, -1],
    [0, -1],
    [-1, -1],
  ];

  // Find the first 1 (starting point)
  let start = null;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (binaryMask[r][c] === 1) {
        start = [r, c];
        break;
      }
    }
    if (start) break;
  }

  if (!start) return []; // No object found

  let contour = [];
  let current = start;
  let prevDir = 0; // Start search from the top-left direction

  do {
    contour.push({ x: current[0], y: current[1] });
    let [r, c] = current;
    let foundNext = false;

    // Start searching from previous direction (to optimize contour tracing)
    for (let i = 0; i < 8; i++) {
      let dirIndex = (prevDir + i) % 8; // Ensuring clockwise search
      let [dr, dc] = directions[dirIndex];
      let nr = r + dr,
        nc = c + dc;

      // Check if inside bounds and is part of the contour
      if (
        nr >= 0 &&
        nr < rows &&
        nc >= 0 &&
        nc < cols &&
        binaryMask[nr][nc] === 1
      ) {
        current = [nr, nc];
        prevDir = (dirIndex + 6) % 8; // Move search direction slightly backward
        foundNext = true;
        break;
      }
    }

    if (!foundNext) break; // If no valid next move, stop tracing
    //TODO: detect multiple contours / make sure multiple contours are being tracked
  } while (current[0] !== start[0] || current[1] !== start[1]);

  return contour;
  // return contour.map(([r, c]) => [c, r]); // Swap (row, col) to (x, y) TODO:FIX ME
}

function simplifyContour(contour: Point[]): Point[] {
  const simplifiedContour = simplify(contour, 5);
  return simplifiedContour;
}

function contourToHull(contour: Point[]): Point[] {
  const contourArray = pointsToArrays(contour);
  console.log(contourArray);
  const hull = convexHull(contourArray); //Array of EDGES
  const hullPoints = hull.map(([p1, p2]) => contour[p1]);
  console.log(hull);
  return hullPoints;
}

function contourToImageData(
  contour: Point[],
  width: number,
  height: number
): ImageData {
  // Create a blank ImageData object (white background)
  const imageData = new ImageData(width, height);
  const data = imageData.data;

  // Fill the background with white (RGBA: 255, 255, 255, 255)
  for (let i = 0; i < data.length; i += 4) {
    data[i] = 255; // Red
    data[i + 1] = 255; // Green
    data[i + 2] = 255; // Blue
    data[i + 3] = 255; // Alpha (fully opaque)
  }

  // Function to plot a pixel in ImageData
  function setPixel(x: number, y: number) {
    if (x >= 0 && x < width && y >= 0 && y < height) {
      const index = (y * width + x) * 4;
      data[index] = 0; // Red
      data[index + 1] = 0; // Green
      data[index + 2] = 255; // Blue
      data[index + 3] = 255; // Alpha
    }
  }

  // Bresenham’s Line Algorithm to draw a line between two points
  function drawLine(p0: Point, p1: Point) {
    let x0 = p0.x,
      y0 = p0.y,
      x1 = p1.x,
      y1 = p1.y;
    let dx = Math.abs(x1 - x0);
    let dy = Math.abs(y1 - y0);
    let sx = x0 < x1 ? 1 : -1;
    let sy = y0 < y1 ? 1 : -1;
    let err = dx - dy;

    while (true) {
      setPixel(x0, y0);
      if (x0 === x1 && y0 === y1) break;
      let e2 = 2 * err;
      if (e2 > -dy) {
        err -= dy;
        x0 += sx;
      }
      if (e2 < dx) {
        err += dx;
        y0 += sy;
      }
    }
  }

  // Draw lines between consecutive points
  for (let i = 0; i < contour.length - 1; i++) {
    drawLine(contour[i], contour[i + 1]);
  }

  // Close the contour by connecting the last point to the first
  if (contour.length > 1) {
    drawLine(contour[contour.length - 1], contour[0]);
  }

  return imageData;
}

function pointsToArrays(points: Point[]): number[][] {
  return points.map(({ x, y }) => [x, y]);
}

function arraysToPoints(arr: number[][]): Point[] {
  return arr.map(([x, y]) => ({ x, y }));
}
