import { blobifyMask } from "../src/blobify.js";
import { readdir, createWriteStream } from "fs";
import path from "path";
import { PNG } from "pngjs";

function pngToImageData(filePath: string): ImageData {
  var img = new Image();
  img.src = filePath;
  const canvas = document.createElement("canvas");
  canvas.height = img.height;
  canvas.width = img.width;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0);
  return ctx.getImageData(0, 0, img.width, img.height);
}

function saveImageDataAsPng(imageData: ImageData, outputPath: string): void {
  const { width, height, data } = imageData;
  const png = new PNG({ width, height });

  for (let i = 0; i < data.length; i++) {
    png.data[i] = data[i];
  }

  const outStream = createWriteStream(outputPath);
  png.pack().pipe(outStream);
}

/**
 * Main function to process all PNGs in a folder.
 * @param inputFolder - The folder containing input PNGs.
 * @param outputFolder - The folder to save processed PNGs.
 */
export async function processPngFolder(
  inputFolder: string,
  outputFolder: string
): Promise<void> {
  readdir(inputFolder, (err, files) => {
    for (const file of files) {
      if (path.extname(file).toLowerCase() === ".png") {
        const inputPath = path.join(inputFolder, file);
        const outputPath = path.join(outputFolder, file);

        console.log(`Processing: ${file}`);
        const imageData = pngToImageData(inputPath);
        const processedData = blobifyMask(imageData);
        saveImageDataAsPng(processedData, outputPath);
      }
    }
  });

  console.log("Processing complete!");
}
