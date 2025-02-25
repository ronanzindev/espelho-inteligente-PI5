import cv2
import face_recognition
import json
import os

DATABASE_FILE = "database.json"

if os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, "r") as f:
        known_faces = json.load(f)
else:
    known_faces = {"names": [], "encodings": []}


def capture_and_save_face():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao acessar a webcam.")
            break

        cv2.imshow("Pressione 's' para salvar", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            print("Salvando rosto...")
            process_face(frame)
            break
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def process_face(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if len(face_locations) == 0:
        print("Nenhum rosto detectado. Tente novamente.")
        return

    face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

    name = input("Digite seu nome: ")

    known_faces["names"].append(name)
    known_faces["encodings"].append(face_encoding.tolist())

    with open(DATABASE_FILE, "w") as f:
        json.dump(known_faces, f)

    print(f"Rosto de {name} salvo com sucesso!")


capture_and_save_face()
