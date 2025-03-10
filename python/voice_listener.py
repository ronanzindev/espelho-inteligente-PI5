import os
from dotenv import load_dotenv
import json
import asyncio
import websockets
import pvporcupine
import pvleopard
import pvrecorder
import wave
import struct
import numpy as np
from openai_client import get_openai_response

load_dotenv()

PICOVOICE_API_KEY = "XBwuWrHCfCSA4COrJXSyZ9/B1xmtbcFVGUD1My9hXbQ0DjHYQmjwxw=="
KEYWORD_PATH = "pvconfig/wake_word_mastigador.ppn"
MODEL_PATH = "pvconfig/porcupine_params_pt.pv"

silence = 3  # 3s de silencio para parar 
max_gravacao = 15  # 15s de gravacao maxima
silence_threshold = 50  # Limiar de silencio

porcupine = pvporcupine.create(
    access_key=PICOVOICE_API_KEY,
    keyword_paths=[KEYWORD_PATH],
    model_path=MODEL_PATH
)

leopard = pvleopard.create(access_key=PICOVOICE_API_KEY)

recorder = pvrecorder.PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

async def send_to_websocket(message):
    async with websockets.connect("ws://localhost:9999") as websocket:
        await websocket.send(message)

def listen_for_keyword():
    print("Escutando a palavra-chave...")
    try:
        recorder.start()
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)
            if result >= 0:
                print("Palavra-chave detectada! Gravando áudio...")
                text = record_audio()
                if text:
                    response = text
                    response = get_openai_response(text)
                    print(f"Resposta da OpenAI: {response}")
                    asyncio.run(send_to_websocket(json.dumps({"type": "voice_response", "response": response})))
    except KeyboardInterrupt:
        print("Parando...")
    finally:
        recorder.delete()
        porcupine.delete()

def record_audio(): #zoou aqui
    frames = []
    silence_frames = 0
    max_silence_frames = int(16000 / 512 * silence)
    max_recording_frames = int(16000 / 512 * max_gravacao)

    print("Gravando áudio...")
    while len(frames) < max_recording_frames:
        pcm = recorder.read()
        frames.extend(pcm)

        volume = np.sqrt(np.mean(np.square(pcm)))

        if volume < silence_threshold:
            silence_frames += 1
        else:
            silence_frames = 0

        if silence_frames >= max_silence_frames:
            print("Silêncio detectado. Parando gravação...")
            break

    print("Parando gravação")

    with wave.open("temp.wav", "wb") as f:
        f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
        f.writeframes(struct.pack("h" * len(frames), *frames))

    text = transcribe_audio("temp.wav")
    os.remove("temp.wav")

    return text

def transcribe_audio(audio_file):
    transcript, words = leopard.process_file(audio_file)
    return transcript

if __name__ == "__main__":
    listen_for_keyword()