import asyncio
import cv2
import face_recognition
import json
import websockets

try:
    with open("database.json", "r") as f:
        known_faces = json.load(f)
except FileNotFoundError:
    known_faces = {"names": [], "encodings": []}


def process_frame(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    recognized_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(
            known_faces["encodings"], face_encoding
        )
        name = "Desconhecido"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_faces["names"][first_match_index]

        recognized_names.append(name)

    return recognized_names


async def recognize_faces(websocket, path=None):
    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            names = process_frame(frame)
            message = json.dumps({"recognized_names": names})

            await websocket.send(message)  # Enviar para o cliente conectado
            await asyncio.sleep(0.5)
    except websockets.ConnectionClosed:
        print("Cliente desconectado")
    finally:
        cap.release()


async def main():
    server = await websockets.serve(
        recognize_faces, "0.0.0.0", 9999
    )  # Aceita conexões de qualquer IP
    print("Servidor WebSocket rodando na porta 9999...")
    await server.wait_closed()


asyncio.run(main())
