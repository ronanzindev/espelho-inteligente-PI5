const NodeHelper = require('node_helper')
const faceapi = require('face-api.js')
const Log = require("logger")
const canvas = require('canvas')
const path = require('path')
const express =require('express')
const {createServer} = require('http')
const {Server} = require('socket.io')

module.exports = NodeHelper.create({
    async start() {
        Log.log(`Starting node helper for: ${this.name}`);
        const { Canvas, Image, ImageData } = canvas;
        faceapi.env.monkeyPatch({ Canvas, Image, ImageData });
        await this.loadModels()
        this.startWebSocketServer()
    },
    async loadModels() {
        try {
            const modelPath = path.join(__dirname, "models");
            await faceapi.nets.tinyFaceDetector.loadFromDisk(modelPath);
            await faceapi.nets.faceLandmark68Net.loadFromDisk(modelPath);
            await faceapi.nets.faceRecognitionNet.loadFromDisk(modelPath);
            await faceapi.nets.faceExpressionNet.loadFromDisk(modelPath);

            Log.log("Modelos do face-api.js carregados com sucesso!");
        } catch (error) {
            Log.error("Erro ao carregar os modelos:", error);
        }
    },
    startWebSocketServer() {
        const app = express();
        const server = createServer(app);
        this.io = new Server(server, { cors: { origin: "*" } });

        this.io.on("connection", (socket) => {
            Log.log("Cliente conectado ao WebSocket");

            socket.on("video_frame", async (data) => {
                const result = await this.processFrame(data);
                socket.emit("face_result", result);
            });
        });

        server.listen(3001, () => {
            Log.log("Servidor WebSocket rodando na porta 3001");
        });
    },

    /**
    * @param {string} imagePath
    */
    async processFrame(base64Image) {
        try {
            const img = await canvas.loadImage(`data:image/jpeg;base64,${base64Image}`);
            const detection = await faceapi.detectSingleFace(img, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks()
                .withFaceExpressions();

            if (detection) {
                return detection.expressions;
            } else {
                return { message: "Nenhum rosto encontrado" };
            }
        } catch (error) {
            Log.error("Erro ao processar frame:", error);
            return { error: "Erro ao processar frame" };
        }
    }
})