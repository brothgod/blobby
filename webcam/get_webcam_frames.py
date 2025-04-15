import cv2

# Open the default webcam (0 = default camera)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Read a single frame
i = 0
while True:
    ret, frame = cap.read()

    if ret:
        # Save the frame to a file
        cv2.imwrite(f"webcam_capture{i}.png", frame)
        print("Image saved as webcam_capture.png")
    else:
        print("Error: Could not read frame.")
    i += 1
# Release the camera

cap.release()
