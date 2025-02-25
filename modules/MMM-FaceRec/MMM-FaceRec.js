Module.register("MMM-FaceRec", {
    defaults: {},
    recognizedNames: [], // Armazena os nomes reconhecidos

    start() {
        Log.log("MMM-FaceRec iniciado!");
        this.sendSocketNotification("TESTE", "TESTE"); // Envia uma notificação de teste
    },

    getDom() {
        const wrapper = document.createElement("div");
        wrapper.className = this.config.classes ? this.config.classes : "thin xlarge bright pre-line";
        if (this.recognizedNames.length > 0) {
            this.recognizedNames.forEach(name => {
                wrapper.innerHTML += `<div>Olá, ${name}</div>`;
            });
        }

        return wrapper;
    },

    socketNotificationReceived: function(notification, payload) {
        Log.log(`Notificação recebida: ${notification}`);
        if (notification === "FACE_RECOGNITION_DATA") {
            Log.log("Rostos reconhecidos:", payload.recognized_names);
            this.recognizedNames = payload.recognized_names;
            this.updateDom();
        }
    },
});
