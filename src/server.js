import express from "express";
import http from "http";
import WebSocket, { WebSocketServer } from "ws";
import path from "path";

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

app.use(express.static("./"));

let masterClient = null; // To track the "master" client (webpage)

wss.on("connection", (socket, req) => {
  const isMaster = req.headers["sec-websocket-protocol"] === "master"; // Check if this is the master client

  if (isMaster) {
    masterClient = socket;
    console.log("Master client connected!");
  } else {
    console.log("External client connected!");
  }

  socket.on("message", (message) => {
    // console.log("Received:", message);
    const parsedMessage = JSON.parse(message);
    // console.log("Parsed message:", parsedMessage);

    // Forward messages from external clients to the master only
    if (
      !isMaster &&
      masterClient &&
      masterClient.readyState === WebSocket.OPEN
    ) {
      masterClient.send(JSON.stringify(parsedMessage));
    }
  });

  socket.on("close", () => {
    if (isMaster) {
      console.log("Master client disconnected!");
      masterClient = null;
    } else {
      console.log("External client disconnected!");
    }
  });
});

const PORT = 3000;
server.listen(PORT, () =>
  console.log(`Server running at http://localhost:${PORT}`)
);
