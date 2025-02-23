Module.register("MMM-FaceRec", {
    defaults: {},
    start() {
        this.socket = io("http://localhost:3001")
        this.videoElement = null
        this.initializeVideoStream()
        this.listenForResults()
    },

    async getDom() {
        const wrapper = document.createElement("div");
        wrapper.innerHTML = "Reconhecimento Facial Ativo";
        this.expressionText = document.createElement("div")
        this.expressionText.style.fontSize = "20px"
        this.expressionText.style.marginTop = "10px"
        wrapper.appendChild(this.expressionText)
        return wrapper;
    },
    initializeVideoStream() {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                const videoElement = document.createElement('video');
                videoElement.srcObject = stream;
                videoElement.play();
                this.startFaceRecognition(videoElement);
            })
            .catch(err => {
                Log.error("Erro ao acessar a câmera:", err);
            });
    },
    startFaceRecognition(videoElement) {
        videoElement.addEventListener("loadeddata", async () => {
            Log.log("Câmera pronta, iniciando reconhecimento...");
            await new Promise(resolve => setTimeout(resolve, 500));
            this.sendFramesToBackend(videoElement)
        });
    },
    initCamera() {
        this.videoElement = document.createElement("video")
        this.videoElement.style = "none";
        document.body.appendChild(this.videoElement)
        navigator.mediaDevices.getUserMedia({ video: true }).then(async (stream) => {
            this.videoElement.srcObject = stream
            this.videoElement.play()
            await this.startFaceRecognition(this.videoElement)
        }).catch((error) => console.error("Erro ao acessar webcam:", error));
    },
    sendFramesToBackend(videoElement) {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        setInterval(() => {
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight
            ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height)
            const base64Image = canvas.toDataURL("image/jpeg").split(",")[1];
            this.socket.emit("video_frame", base64Image)
        }, 500)
    },
    listenForResults() {
        this.socket.on("face_result", (result) => {
            if (result && typeof result === "object") {
                const expressions = Object.entries(result)
                const [strongestExpression, confidence] = expressions.reduce((max, current) => current[1] > max[1] ? current : max)
                console.log(strongestExpression)
                let message = ""
                switch (strongestExpression) {
                    case "happy":
                        message = "Você parece feliz! 😊";
                        break;
                    case "sad":
                        message = "Você está triste 😢";
                        break;
                    case "angry":
                        message = "Parece que você está bravo! 😡";
                        break;
                    case "surprised":
                        message = "Você está surpreso! 😲";
                        break;
                    case "neutral":
                        message = "Você está neutro. 😐";
                        break;
                    default:
                        message = "Expressão não reconhecida";
                }
                this.expressionText.innerHTML = message
            } else {
                this.expressionText.innerHTML = "Nenhuma expressão detectada.";
            }
        });
    }

})