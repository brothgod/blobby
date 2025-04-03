#!/bin/bash

echo "Starting project..."

# Run npm build (blocking)
npm run build

# Start background processes and track their PIDs
npm run dev & DEV_PID=$!
node src/server.js & NODE_PID=$!
python webcam/WebcamController.py & WEBCAM_PID=$!

# Function to handle termination (Ctrl+C or script exit)
cleanup() {
    echo "Stopping all processes..."
    kill $DEV_PID $NODE_PID $WEBCAM_PID
    wait $DEV_PID $NODE_PID $WEBCAM_PID 2>/dev/null
    echo "All processes stopped."
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM (kill command)
trap cleanup SIGINT SIGTERM

# Keep script running to manage background processes
echo "All processes started. Press Ctrl+C to stop."
wait
