enum Orientation {
  ORIG = 0,
  ROT90 = 90,
  ROT180 = 180,
  ROT270 = 270,
}

type TilePattern = Tile[][];
type Tile = {
  canvasIndex: number;
  rotation: Orientation;
};

//Returns an array of list tuples, representing what canvas to put in each grid, (canvas, rotation)[]
export const generateTilePattern = (
  numWebcams: number,
  rows: number,
  cols: number,
  patternIndex: number
): TilePattern => {
  return pattern1(numWebcams, rows, cols);
};

//Alternating pattern
const pattern1 = (
  numWebcams: number,
  rows: number,
  cols: number
): TilePattern => {
  const ret: TilePattern = Array.from({ length: rows }, () =>
    Array(cols).fill({ canvasIndex: -1, rotation: Orientation.ORIG })
  );

  let counter = 0;
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      ret[i][j] = { canvasIndex: counter, rotation: Orientation.ORIG };
      counter = (counter + 1) % numWebcams;
    }
  }
  return ret;
};

export const buildCanvasGrid = (
  tilePattern: TilePattern,
  numWebcams: number,
  canvasContainer: HTMLDivElement
): CanvasRenderingContext2D[][] => {
  //This function should....
  //Add canvases to the DOM in the order that is required by the pattern
  //Apply rotations as necessary (not for MVP)
  //Return the ctxs separated by index
  const ctxLists: CanvasRenderingContext2D[][] = Array.from(
    { length: numWebcams },
    () => []
  );

  const childrenList: HTMLCanvasElement[] = [];

  for (let i = 0; i < tilePattern.length; i++) {
    for (let j = 0; j < tilePattern[0].length; j++) {
      let tile = tilePattern[i][j];
      let canvas = document.createElement("canvas");
      canvas.classList.add(`canvas-${tile.canvasIndex}`);
      canvas.style.height = "100%";
      canvas.style.width = "100%";
      let ctx = canvas.getContext("2d")!;
      ctxLists[tile.canvasIndex].push(ctx);
      childrenList.push(canvas);
    }
  }
  canvasContainer.replaceChildren(...childrenList); // Clears all children

  return ctxLists;
};
