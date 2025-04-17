# blobby

## To run

3 terminals are needed:

1.  `npm run build`
    `npm run dev`
2.  `node src/server.js`
3.  `python webcam/WebcamController.py`

### Week 7 (3/5-3/12)

- Added websocket control
- Websocket middleman relays blob points from Python script to website, which displays it
- Multiple webcams
- Filled in shape

### Week 8/9 (3/12-3/4/2)

- Added multiple canvases
- Added "master" canvas and worker model
- Added constants.yaml

### Week 10 (4/2-4/9)

- Changed threading to multiprocessing
- Changed yaml to json
- Added start script
- Tested with two webcams, it worked!!
- Alternated canvases
- Added canvas patterns

### Week 11 (4/9 - 4/16)

- Added latest canvas behavior to webworker
- Testing image mode
- Added open visual testing
- Added test functionalities

### TODO:

- Fix jittering!!
- Add a benchmark for FPS
- Add a way to test blobbing
- Fix issue where detect_async gets overwhelmed with frames (switch to image mode?)
- Add more patterns + number options to switch it
- Look into if Worker model is actually necessary
- Add a way to test the blobificatino function
