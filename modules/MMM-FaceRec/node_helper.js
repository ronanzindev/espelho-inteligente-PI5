const NodeHelper = require('node_helper')
const Log = require("logger")
const WebSocket = require("ws")

module.exports = NodeHelper.create({
    async start() {
        Log.log(`Starting node helper for: ${this.name}`);
        this.startWebSocketClient()
        this.notifyAAA()
    },
    notifyAAA() {
        Log.log("Enviando notificação TESTE"); // Log para verificar se a notificação está sendo enviada
        this.sendSocketNotification("TESTE", "TESTE");
    },
    startWebSocketClient() {
        const ws = new WebSocket("ws://127.0.0.1:9999")
        ws.on("open", () => {
            Log.info("Conectado ao servidor websocket")
        })
        ws.on("message", (data) => {
            try {
                const parsedData = JSON.parse(data);
                this.sendSocketNotification("FACE_RECOGNITION_DATA", parsedData);
            }catch(ex) {
                Log.error("Erro ao processar mensagem do WebSocket:", error);
            }
        })
        ws.on("error", (error) => {
            Log.error("Erro no WebSocket:", error);
        });

        ws.on("close", () => {
            Log.log("WebSocket fechado. Tentando reconectar em 5 segundos...");
            setTimeout(() => this.startWebSocketClient(), 5000);
        });

    },
})