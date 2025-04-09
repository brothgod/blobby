# blobby

## To run

3 terminals are needed:

1.  `npm run build`
    `npm run dev`
2.  `node src/server.js`
3.  `python webcam/WebcamController.py`

### Week 7

- Added websocket control
- Websocket middleman relays blob points from Python script to website, which displays it
- Multiple webcams
- Filled in shape

### Week 8/9

- Added multiple canvases
- Added "master" canvas and worker model
- Added constants.yaml

### Week 10

- Changed threading to multiprocessing
- Changed json to yaml
- Tested with two webcams, it worked!!
- Alternated canvases

### TODO:

- Fix jittering!!
- Add a benchmark for FPS
- Add a way to test blobbing
- Fix issue where detect_async gets overwhelmed with frames (switch to image mode?)
- Add more patterns + number options to switch it
- Look into if Worker model is actually necessary
