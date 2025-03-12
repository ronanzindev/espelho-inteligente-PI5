import whisper
import pyaudio
import wave
# from TTS.api import TTS
import numpy as np
import os
from openai_client import get_openai_response
import warnings
import pyttsx3

warnings.filterwarnings("ignore", category=UserWarning)

def falar_texto(texto):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.say(texto)
    engine.runAndWait()


# Configuração do microfone
CHUNK = 1024  # Tamanho do bloco de áudio
FORMAT = pyaudio.paInt16  # Formato do áudio
CHANNELS = 1  # Mono
RATE = 16000  # Taxa de amostragem (Whisper funciona melhor em 16kHz)
RECORD_SECONDS = 5  # Tempo de gravação
WAVE_OUTPUT_FILENAME = os.path.join(os.getcwd(), "temp_audio.wav")

def perguntar():
    # Inicializar PyAudio
    audio = pyaudio.PyAudio()

    # Abrir stream de áudio
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Gravando...")

    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Gravação finalizada.")

    # Fechar stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Salvar o áudio em um arquivo WAV
    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    # Carregar Whisper e transcrever áudio gravado
    model = whisper.load_model("base")
    result = model.transcribe(WAVE_OUTPUT_FILENAME)
    print("Texto reconhecido:", result["text"])
    resposta = get_openai_response(result["text"])
    print(resposta)
    falar_texto(resposta)