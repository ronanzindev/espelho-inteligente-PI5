Module.register("MMM-FaceRec", {
    defaults: {},
    recognizedNames: [], //
    emotion: "",
    emotions: {
        "sad": "triste",
        "neutral": "normal",
        "happy": "feliz",
        "fear": "com medo"
    },
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
        wrapper.innerHTML += `${this.emotions[this.emotion] ? `<div>Você está ${this.emotions[this.emotion]}.</div>` : ''}`
        return wrapper;
    },

    socketNotificationReceived: function(notification, payload) {
        if (notification === "FACE_RECOGNITION_DATA") {
            if(payload.data) {
                this.recognizedNames = payload.data.names
                this.emotion = payload.data.emotion
                this.updateDom();
            }
        }
    },
});
