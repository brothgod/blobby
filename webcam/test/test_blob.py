from ..Webcam import Webcam
import os

folder_path = "test/input_images"  # change this to your folder path

a = Webcam()

for filename in os.listdir(folder_path):
    if filename.endswith(".png"):
        file_path = os.path.join(folder_path, filename)
        # Do something with the image
        with Image.open(file_path) as img:
            a._process_image(folder_path)
            print(f"Processing {filename}...")
            # Example: convert to grayscale
            grayscale = img.convert("L")
            # Save or process as needed
            # grayscale.save(os.path.join(folder_path, f"gray_{filename}"))
