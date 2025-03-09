import asyncio
import cv2
import face_recognition
import json
import websockets
from deepface import DeepFace

try:
    with open("database.json", "r") as f:
        known_faces = json.load(f)
except FileNotFoundError:
    known_faces = {"names": [], "encodings": []}

def process_frame(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    data = {"names": [], "emotion": ""}
    names = []
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_faces["encodings"], face_encoding)
        name = "Desconhecido"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_faces["names"][first_match_index]

        face_crop = frame[top:bottom, left:right] # frame do rosto
        try:
            analysis = DeepFace.analyze(face_crop, actions=['emotion'], enforce_detection=False)
            emotion = analysis[0]['dominant_emotion']
        except:
            emotion = "desconhecido"
        data["emotion"] = emotion
        names.append(name)
        data["names"] = names
    return data

async def recognize_faces(websocket, path = None):
    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            data = process_frame(frame)
            message = json.dumps({"data": data})

            await websocket.send(message)
            await asyncio.sleep(0.5)
    except websockets.ConnectionClosed:
        print("Cliente desconectado")
    finally:
        cap.release()

async def main():
    server = await websockets.serve(recognize_faces, "0.0.0.0", 9999)  # Aceita conexões de qualquer IP
    print("Servidor WebSocket rodando na porta 9999...")
    await server.wait_closed()

asyncio.run(main())
